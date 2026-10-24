"""Quota metadata, bounded waits and same-host coordination; declared transport."""
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from minder_app.model_gateway import CoordinatedGroq, QuotaError, duration, coordination_directory


class Response(io.BytesIO):
    status=200
    headers={'x-ratelimit-limit-tokens':'8000','x-ratelimit-remaining-tokens':'7000',
        'x-ratelimit-reset-tokens':'1.2s','authorization':'must-not-be-recorded'}


def response():
    return Response(json.dumps(dict(choices=[dict(message=dict(content='A declared transport reply.'))],
        usage=dict(prompt_tokens=20,completion_tokens=8,total_tokens=28))).encode())


class GatewayTests(unittest.TestCase):
    def test_linux_uses_writable_temp_and_macos_preserves_existing_group(self):
        from unittest.mock import patch
        with patch.dict('os.environ',{},clear=True),patch('os.getuid',return_value=123):
            with patch('os.path.isdir',return_value=False),patch('tempfile.gettempdir',return_value='/tmp'):
                self.assertEqual(str(coordination_directory()),'/tmp/minder-provider-coordination-123')
            with patch('os.path.isdir',return_value=True):
                self.assertEqual(str(coordination_directory()),'/private/tmp/minder-provider-coordination-123')

    def test_local_completion_reservation_queues_before_any_outbound_call(self):
        calls=[]
        with tempfile.TemporaryDirectory() as root:
            p=CoordinatedGroq(key='declared-test',model='declared-model',coordination_dir=root,
                max_wait=0,opener=lambda *a,**k:calls.append(1))
            p.state_path.write_text(json.dumps(dict(completion_budget=dict(used=950,at=time.time()))))
            with self.assertRaises(QuotaError) as caught:p.complete([])
            self.assertEqual(caught.exception.public()['transport_attempts'],0)
            self.assertGreater(caught.exception.public()['retry_after_seconds'],10)
            self.assertEqual(calls,[])

    def test_duration_header_units_and_allowlist(self):
        self.assertEqual(duration('1m26.4s'),86.4)
        self.assertEqual(duration('250ms'),.25)
        with tempfile.TemporaryDirectory() as root:
            provider=CoordinatedGroq(key='declared-test',model='declared-model',coordination_dir=root,opener=lambda *a,**k:response())
            result=provider.complete([dict(role='user',content='A test')])
            self.assertEqual(result['transport_attempts'],1)
            self.assertEqual(result['quota_header_scope']['tokens'],'tokens_per_minute')
            self.assertNotIn('authorization',json.dumps(json.loads(provider.state_path.read_text())))
            self.assertNotIn('declared-test',provider.state_path.read_text())

    def test_two_instances_serialize_and_queue_is_bounded(self):
        active=0;maximum=0;lock=threading.Lock()
        def transport(*a,**k):
            nonlocal active,maximum
            with lock:active+=1;maximum=max(maximum,active)
            time.sleep(.08)
            with lock:active-=1
            return response()
        with tempfile.TemporaryDirectory() as root:
            providers=[CoordinatedGroq(key='declared-test',model='declared-model',coordination_dir=root,opener=transport) for _ in range(2)]
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda p:p.complete([dict(role='user',content='test')]),providers))
            self.assertEqual(maximum,1)
            self.assertTrue(any(r['queue_ms']>=50 for r in results))
            with providers[0].flight(1):
                providers[1].max_wait=0
                with self.assertRaises(QuotaError) as caught:providers[1].complete([])
                self.assertEqual(caught.exception.code,'provider_queue_busy')

    def test_quota_cooldown_makes_no_outbound_call_and_429_is_not_retried(self):
        calls=[]
        def limited(*a,**k):
            calls.append(1)
            raise HTTPError('https://api.groq.com/openai/v1/chat/completions',429,'rate limited',
                {'retry-after':'30','x-ratelimit-remaining-tokens':'0','x-ratelimit-reset-tokens':'30s'},None)
        with tempfile.TemporaryDirectory() as root:
            p=CoordinatedGroq(key='declared-test',model='declared-model',coordination_dir=root,opener=limited,max_wait=0)
            with self.assertRaises(QuotaError) as caught:p.complete([])
            self.assertEqual(caught.exception.code,'provider_rate_limited')
            self.assertGreater(caught.exception.public()['retry_after_seconds'],29)
            with self.assertRaises(QuotaError):p.complete([])
            self.assertEqual(len(calls),1)
