"""A HTTP/schema integration over D services; synthetic owners/software turn handler."""
import json
from pathlib import Path
import tempfile
from jsonschema import Draft202012Validator
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.integration_cli import wsgi_request


def main():
    out = Path('ml/artifacts/session-a/product/morning')
    schema = json.loads(Path('docs/execution/product-v2/contracts.schema.json').read_text())

    def check(kind, value):
        Draft202012Validator(dict(schema, **{'$ref': '#/$defs/' + kind})).validate(value)

    with tempfile.TemporaryDirectory(dir=out) as tmp:
        app, _ = build('A', database=Path(tmp) / 'contracts.sqlite3', role_ids=['onet:15-1252.00'])
        # This acceptance exercises HTTP ownership/schema/state, not real model behavior.
        app.conversation_turn_handler = lambda *args: dict(answer='Synthetic visible assistant answer')
        owner1 = wsgi_request(app, 'POST', '/api/session', {})[1]['token']
        owner2 = wsgi_request(app, 'POST', '/api/session', {})[1]['token']

        def call(method, path, body=None, *, token=owner1, expected=200):
            status, value = wsgi_request(app, method, '/api/' + path, body or {}, token)
            assert status == expected, (path, status, value.get('code'))
            return value

        assert wsgi_request(app, 'GET', '/api/product/bot-preferences')[0] == 401
        profile = call('PUT', 'profile', dict(profile=dict(synthetic=True), expected_version=None))
        singleton = call('GET', 'product/mindbot-conversation')['conversation']['conversation_id']
        schedule = call('PUT', 'agent-settings', dict(settings=dict(state='paused'), expected_version=None))
        default = call('GET', 'product/bot-preferences')
        check('BotPreferencesResult', default)
        assert not default['configured'] and default['preferences']['version'] is None
        saved = call('PUT', 'product/bot-preferences', dict(display_name='  Study Buddy  ',
            avatar_id='frog-rose', expected_version=None))
        check('BotPreferencesResult', saved)
        assert saved['configured'] and saved['preferences']['display_name'] == 'Study Buddy'
        assert call('GET', 'product/bot-preferences') == saved
        assert not call('GET', 'product/bot-preferences', token=owner2)['configured']
        call('PUT', 'product/bot-preferences', dict(display_name='Foreign version', avatar_id='nimo-blue',
            expected_version=saved['preferences']['version']), token=owner2, expected=409)
        call('PUT', 'product/bot-preferences', dict(display_name='Stale save', avatar_id='nimo-blue',
            expected_version=None), expected=409)
        call('PUT', 'product/bot-preferences', dict(display_name='Invalid URL',
            avatar_id='https://example.invalid/avatar', expected_version=saved['preferences']['version']), expected=422)
        assert call('GET', 'profile')['version'] == profile['version']
        assert call('GET', 'agent-settings') == schedule
        assert call('GET', 'product/mindbot-conversation')['conversation']['conversation_id'] == singleton

        def create(title, key, token=owner1):
            return call('POST', 'product/conversations', dict(title=title, idempotency_key=key), token=token)['conversation']['conversation_id']

        target = create('Synthetic older history', 'target')
        for index in range(51):
            call('POST', 'product/conversation-turn', dict(conversation_id=target,
                message='Synthetic later-message needle' if index == 50 else 'Synthetic ordinary message',
                idempotency_key='fixture-' + str(index), expected_profile_version=profile['version']))
        opened = call('POST', 'product/conversation', dict(conversation_id=target))
        assert opened['has_more'] and len(opened['messages']) == 100
        assert not any('later-message needle' in m['content'] for m in opened['messages'])
        percent = create('Synthetic % literal', 'percent')
        unicode = create('Synthetic Straße', 'unicode')
        create('Synthetic later-message needle', 'foreign', owner2)
        deleted = create('Synthetic later-message needle', 'deleted')
        call('DELETE', 'product/conversation', dict(conversation_id=deleted, idempotency_key='delete'))
        call('POST', 'product/conversation-turn', dict(conversation_id=singleton,
            message='Synthetic later-message needle', idempotency_key='bot-excluded', expected_profile_version=profile['version']))

        def search(query, **kwargs):
            result = call('POST', 'product/conversations-search', dict(query=query, **kwargs))
            check('ConversationSearchResult', result)
            return result

        assert [c['conversation_id'] for c in search('later-message needle')['conversations']] == [target]
        assert [c['conversation_id'] for c in search('%')['conversations']] == [percent]
        assert [c['conversation_id'] for c in search('STRASSE')['conversations']] == [unicode]
        first = search('', limit=1)
        assert first['has_more'] and first['next_offset'] == 1
        second = search('', limit=1, offset=first['next_offset'])
        assert first['conversations'][0]['conversation_id'] != second['conversations'][0]['conversation_id']
        assert call('GET', 'action-history')['history'] == []
        report = dict(status='passed', runtime_revision=app.runtime_revision,
            evidence='Actual WSGI/auth/routes/schema and SQLite services; two synthetic local owners, explicit software conversation handler, no live login or model claim',
            checks=['read-only identity defaults', 'trimmed saved name', 'approved avatar only',
                'stale and foreign versions rejected', 'Profile/singleton/schedule preserved',
                'owned active Minder only', 'message beyond first100 searched', 'literal wildcard',
                'Unicode casefold', 'paged metadata/schema', 'zero actions'])
        (out / 'ux-state-integration.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
