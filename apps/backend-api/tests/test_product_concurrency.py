"""Real HTTP concurrency with explicitly delayed synthetic provider, no real model."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server, WSGIServer
from support import AppCase
from minder_ml.intelligence.product_runtime import ProductServer, QuietHandler


class DelayedProvider:
    model = 'explicit-delayed-software-provider'
    def __init__(self, delay):
        self.delay, self.started = delay, threading.Event()
    def complete_tool(self, messages, tool):
        self.started.set()
        time.sleep(self.delay)
        ids = tool['function']['parameters']['properties']['statement_ids']['items']['enum']
        return dict(status='available',text=json.dumps({'statement_ids':[ids[0]]}),
                    model=self.model,request_id='software-delay-only')


class ProductConcurrencyTests(AppCase):
    def server(self, server_class):
        server=make_server('127.0.0.1',0,self.app,server_class=server_class,handler_class=QuietHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(lambda:(server.shutdown(),thread.join(timeout=5),server.server_close()))
        return 'http://127.0.0.1:'+str(server.server_port)

    def request(self, base, path, body=None, token=None):
        request=Request(base+'/api/'+path,data=json.dumps(body).encode() if body is not None else None,
            headers={'Content-Type':'application/json','Authorization':'Bearer '+(token or self.token)})
        with urlopen(request,timeout=5) as response:
            return json.loads(response.read())

    def delay_read(self, server_class, delay=.5):
        p=self.save();provider=DelayedProvider(delay);self.app.provider=provider
        base=self.server(server_class)
        with ThreadPoolExecutor(max_workers=2) as pool:
            pending=pool.submit(self.request,base,'chat',dict(message='Explain market evidence',expected_profile_version=p['version']))
            self.assertTrue(provider.started.wait(2))
            start=time.perf_counter();saved=self.request(base,'agents');elapsed=time.perf_counter()-start
            self.assertIn('events',saved);pending.result(timeout=4)
        return elapsed

    def test_threaded_saved_read_completes_while_chat_is_pending(self):
        elapsed=self.delay_read(ProductServer)
        self.assertLess(elapsed,.35)

    def test_serial_baseline_exhibits_same_head_of_line_block(self):
        elapsed=self.delay_read(WSGIServer)
        self.assertGreater(elapsed,.4)

    def test_concurrent_duplicate_direct_action_applies_exactly_once(self):
        plan,request=self.setup_request();base=self.server(ProductServer)
        body=dict(request=request,idempotency_key='concurrent-identical-request')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.request(base,'direct-action',body),range(2)))
        self.assertEqual(results[0],results[1])
        history=self.request(base,'action-history')['history']
        self.assertEqual(len(history),1)
        self.assertEqual(len(results[0]['target']['progress_event_ids']),1)
        self.assertFalse(results[0]['target']['tasks'][0]['mastery_verified'])
        other=self.store.session()['token']
        self.assertEqual(self.request(base,'action-history',token=other)['history'],[])


if __name__ == '__main__':
    import unittest
    unittest.main()
