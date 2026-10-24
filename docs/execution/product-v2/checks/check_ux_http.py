"""Actual A listener settings/search smoke; synthetic owners, zero chat/provider calls."""
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def main():
    base = 'http://127.0.0.1:9111/api/'

    def call(method, path, body=None, token=None, expected=200):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = Request(base + path, headers=headers, method=method,
            data=None if body is None else json.dumps(body).encode())
        try:
            response = urlopen(request, timeout=10)
        except HTTPError as error:
            assert error.code == expected, (path, error.code)
            return json.load(error)
        with response:
            assert response.status == expected
            return json.load(response)

    health = call('GET', 'health')
    token = call('POST', 'session', {})['token']
    other = call('POST', 'session', {})['token']
    call('GET', 'product/bot-preferences', expected=401)
    profile = call('PUT', 'profile', dict(profile=dict(synthetic=True), expected_version=None), token)
    singleton = call('GET', 'product/mindbot-conversation', token=token)['conversation']['conversation_id']
    default = call('GET', 'product/bot-preferences', token=token)
    assert not default['configured']
    saved = call('PUT', 'product/bot-preferences', dict(display_name='  Synthetic Buddy  ',
        avatar_id='star-yellow', expected_version=None), token)
    assert saved['preferences']['display_name'] == 'Synthetic Buddy'
    assert call('GET', 'product/bot-preferences', token=token) == saved
    assert not call('GET', 'product/bot-preferences', token=other)['configured']
    call('PUT', 'product/bot-preferences', dict(display_name='Stale', avatar_id='nimo-blue',
        expected_version=None), token, expected=409)
    assert call('GET', 'profile', token=token)['version'] == profile['version']
    assert call('GET', 'product/mindbot-conversation', token=token)['conversation']['conversation_id'] == singleton
    call('GET', 'agent-settings', token=token, expected=404)
    created = call('POST', 'product/conversations', dict(title='Synthetic owned résumé',
        idempotency_key='own-search'), token)['conversation']['conversation_id']
    call('POST', 'product/conversations', dict(title='Synthetic owned résumé', idempotency_key='foreign'), other)
    results = call('POST', 'product/conversations-search', dict(query='RÉSUMÉ'), token)
    assert [c['conversation_id'] for c in results['conversations']] == [created]
    assert results['search_scope'] == 'title_and_visible_messages'
    assert call('GET', 'action-history', token=token)['history'] == []
    report = dict(status='passed', runtime_revision=health['runtime_revision'], actual_HTTP=True,
        base=base, synthetic_local_owners=2, actual_save_reload=True, trimmed_name=True,
        stale_rejected=True, cross_owner_identity_and_search_isolated=True,
        profile_singleton_preserved=True, schedule_not_created=True,
        provider_turns_requested=0, action_history_records=0, live_Clerk_claim=False)
    Path('ml/artifacts/session-a/product/morning/ux-http.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
