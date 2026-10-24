"""Real local timer acceptance: no browser, forged clock, manual tick or provider."""
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


def main():
    base = 'http://127.0.0.1:9111/api/'
    token = None

    def call(path, body=None, method=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        with urlopen(Request(base + path, headers=headers,
                            data=None if body is None else json.dumps(body).encode(),
                            method=method or ('GET' if body is None else 'POST')),
                     timeout=10) as response:
            return json.load(response)

    health = call('health')
    assert health['local_worker_running'] is True
    token = call('session', {})['token']
    profile = call('profile', {'profile': {'synthetic': True,
        'career_context': {'goals': 'Synthetic no-task daily timer acceptance'}},
        'expected_version': None}, 'PUT')
    original = call('product/mindbot-conversation')
    # Leave at least 20s to save before the genuine upcoming wall-clock minute.
    due_local = (datetime.now(ZoneInfo('Asia/Kuala_Lumpur')) + timedelta(seconds=80)).replace(second=0, microsecond=0)
    settings = call('agent-settings', {'settings': {'enabled': True,
        'check_time': due_local.strftime('%H:%M'), 'timezone': 'Asia/Kuala_Lumpur',
        'scope': {'plan_ids': []}}, 'expected_version': None}, 'PUT')
    due = datetime.fromisoformat(settings['next_run'].replace('Z', '+00:00'))
    assert 15 < (due - datetime.now(timezone.utc)).total_seconds() < 85
    # The existing supervisor drains one event per30s, including older state events.
    # Allow that bounded queue to drain; record actual lateness, not a fake due clock.
    deadline = time.monotonic() + 360
    result = None
    while time.monotonic() < deadline:
        saved = call('agent-settings')
        if saved.get('last_result'):
            result = saved
            break
        time.sleep(3)
    assert result is not None, 'real background worker did not record the due event'
    assert result['last_result']['status'] == 'processed', result['last_result']
    after = call('product/mindbot-conversation')
    assert after['conversation']['conversation_id'] == original['conversation']['conversation_id']
    assert len(after['messages']) == len(original['messages']) + 1
    assert result['last_result']['message_id'] == after['messages'][-1]['message_id']
    # Cross another actual supervisor poll. Never invoke Worker.tick in this check.
    time.sleep(32)
    assert call('product/mindbot-conversation')['messages'] == after['messages']
    assert call('profile')['version'] == profile['version']
    assert call('action-history')['history'] == []
    assert call('plans')['plans'] == []
    paused = call('agent-settings', {'settings': {'state': 'paused'},
        'expected_version': result['version']}, 'PUT')
    assert paused['next_run'] is None
    report = dict(runtime_revision=health['runtime_revision'], actual_local_timer=True,
        browser_open=False, synthetic_owner=True, forged_clock=False, manual_tick=False,
        provider_needed=False, persisted_due=due.isoformat(),
        actual_result=result['last_result'], same_singleton=True, added_messages=1,
        due_lateness_seconds=round((datetime.fromisoformat(
            result['last_result']['observed_at'].replace('Z', '+00:00')) - due).total_seconds(), 3),
        repeat_poll_added_messages=0, task_action_profile_changes=0,
        paused_after_check=True, hosted_acceptance=False)
    target = Path('ml/artifacts/session-a/product/morning/live-local-worker.json')
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
