"""Actual A HTTP/Qwen action, exact replay and concurrent reads; synthetic owner."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen


def main():
    base = 'http://127.0.0.1:9111/api/'
    token = None

    def call(path, body=None, method=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        start = time.perf_counter()
        with urlopen(Request(base + path, headers=headers,
                            data=None if body is None else json.dumps(body).encode(),
                            method=method or ('GET' if body is None else 'POST')),
                     timeout=50) as response:
            return json.load(response), round((time.perf_counter() - start) * 1000, 3)

    token = call('session', {})[0]['token']
    health = call('health')[0]
    profile = call('profile', {'profile': {'synthetic': True,
        'career_context': {'goals': 'Learn software development through practice'}},
        'expected_version': None}, 'PUT')[0]
    conversation = call('product/mindbot-conversation')[0]
    cid = conversation['conversation']['conversation_id']
    body = dict(conversation_id=cid, idempotency_key='synthetic-explicit-availability',
        expected_profile_version=profile['version'],
        message='Please set my study availability to 6 hours per week.')
    reads = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        pending = executor.submit(call, 'product/conversation-turn', body)
        time.sleep(.05)
        for _ in range(3):
            was_pending = not pending.done()
            saved, elapsed = call('profile')
            reads.append(dict(elapsed_ms=elapsed, provider_turn_pending_at_start=was_pending))
            assert saved['profile_id'] == profile['profile_id']
        first, elapsed = pending.result()
    response = first['response']
    folder = Path('ml/artifacts/session-a/product/morning')
    report = dict(runtime_revision=health['runtime_revision'], synthetic=True, mocked=False,
        elapsed_ms=elapsed, provider=response.get('provider'), reads=reads,
        response_mode=response.get('response_mode'), action_status=response.get('action_status'))
    (folder / 'live-action-attempt.json').write_text(json.dumps(report, indent=2) + '\n')
    assert response['provider']['status'] == 'available', response.get('provider')
    assert response['action_status'] == 'applied', response.get('action_status')
    after = call('profile')[0]
    availability = [c for c in after['constraints'] if c['scope'] == 'weekly_hours']
    assert len(availability) == 1 and availability[0]['value'] == 6
    assert availability[0]['unit'] == 'hours_per_week'
    assert after['evidence'] == profile['evidence']
    replay = call('product/conversation-turn', body)[0]
    assert replay['response'] == response
    assert call('profile')[0]['version'] == after['version']
    history = call('action-history')[0]['history']
    assert len(history) == 1
    loaded = call('product/mindbot-conversation')[0]
    assert loaded['conversation']['conversation_id'] == cid
    assert len(loaded['messages']) == 2
    assert any(r['provider_turn_pending_at_start'] for r in reads)
    report.update(exact_replay_one_action=True, same_mindbot=True,
        saved_weekly_hours=6, skill_evidence_unchanged=True, stored_messages=2)
    (folder / 'live-action.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
