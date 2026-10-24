"""A's exact asset/schema/registry handoff; no claim D services are implemented."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from minder_ml.intelligence.policy import ROOT
from minder_app.product_routes import ROUTES


def main():
    root = ROOT / 'docs/execution/product-v2'
    public = json.loads((root / 'contracts.schema.json').read_text())
    Draft202012Validator.check_schema(public)
    avatars = json.loads((root / 'BOT_AVATARS.v1.json').read_text())
    assert len(avatars['avatars']) == 25
    ids = public['$defs']['BotAvatarId']['enum']
    assert ids == [a['avatar_id'] for a in avatars['avatars']]
    for item in avatars['avatars']:
        assert hashlib.sha256((ROOT / item['source_path']).read_bytes()).hexdigest() == item['sha256']
    manifest = json.loads((root / 'HOME_ASSET_HANDOFF.json').read_text())
    for item in manifest['imported_files']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']

    def check(kind, value):
        Draft202012Validator(dict(public, **{'$ref': '#/$defs/' + kind})).validate(value)

    for identifier in ids:
        check('BotPreferencesWrite', dict(display_name='Study Buddy', avatar_id=identifier, expected_version=None))
    check('BotPreferencesResult', dict(contract_version='bot-preferences-v1', configured=False,
        preferences=dict(display_name='My Bot', avatar_id='nimo-blue', version=None)))
    for name in ('', ' ', ' Name', 'Name ', 'x' * 41, 'x\nName', 'x\x7fName'):
        try:
            check('BotPreferencesWrite', dict(display_name=name, avatar_id='nimo-blue', expected_version=None))
        except ValidationError:
            pass
        else:
            raise AssertionError('invalid normalized identity accepted')
    for value in ('https://example.invalid/avatar.png', '../nimo-blue', 'unknown'):
        try:
            check('BotPreferencesWrite', dict(display_name='My Bot', avatar_id=value, expected_version=None))
        except ValidationError:
            pass
        else:
            raise AssertionError('unapproved avatar accepted')
    check('ConversationSearch', dict(query='notebook', limit=20, offset=0))
    check('ConversationSearchResult', dict(contract_version='conversation-search-v1', query='notebook',
        search_scope='title_and_visible_messages', conversations=[], offset=0, limit=20,
        has_more=False, next_offset=None))
    assert ROUTES['GET', '/api/product/bot-preferences'] == 'bot_preferences'
    assert ROUTES['PUT', '/api/product/bot-preferences'] == 'bot_preferences'
    assert ROUTES['POST', '/api/product/conversations-search'] == 'conversations'
    print('Exact25avatar hashes,25Home/brief hashes, strict schemas and route registry passed. D runtime implementation remains a separate handoff.')


if __name__ == '__main__':
    main()
