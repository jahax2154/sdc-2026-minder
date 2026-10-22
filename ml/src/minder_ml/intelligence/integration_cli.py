"""Session A local integration binding/evidence over committed owner modules.

Run smoke --output ml/artifacts/session-a/<new-directory>, or serve on A's
reserved API port. Never uses fixture providers, production DBs or other lanes.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys

from .catalogue_service import OccupationalCatalogue
from .personal_service import PersonalMatchingService
from .policy import ROOT


def role_aliases(catalogue):
    """Exact source identity projection, not an inferred taxonomy crosswalk."""
    return {r['role_id']: catalogue.reference(r['role_id'])['occupation']['O*NET-SOC Code']
            for r in catalogue.roles()}


def application(database, *, role_ids=None):
    # C's stdlib package lives in its owned app path in THIS worktree.
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.api import Application
    from minder_app.store import Store
    from .app_context import CareerServices
    database = Path(database).resolve()
    if not database.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('integration DB must be isolated under Session A artifacts')
    catalogue = OccupationalCatalogue()
    roles = catalogue.roles() if role_ids is None else [catalogue.role(rid) for rid in role_ids]
    services = CareerServices(PersonalMatchingService(), roles=roles,
                              sources=catalogue.coverage['sources'], mode='local_source_services')
    return Application(Store(database), services), catalogue


def wsgi_request(app, method, path, body=None, token=''):
    """Exercise the actual public WSGI serialization/error/auth boundary."""
    raw = json.dumps(body).encode() if body is not None else b''
    captured = {}
    def start_response(status, headers):
        captured['status'] = int(status.split()[0])
    response = b''.join(app(dict(REQUEST_METHOD=method, PATH_INFO=path,
                                CONTENT_LENGTH=str(len(raw)), **{'wsgi.input': io.BytesIO(raw)},
                                HTTP_AUTHORIZATION='Bearer ' + token), start_response))
    return captured['status'], json.loads(response)


def smoke(output):
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('evidence must stay in Session A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    # Explicitly selected exploration view, not a three-role runtime allowlist.
    selected = ['onet:15-1252.00', 'onet:11-1011.00']
    app, catalogue = application(output / 'runtime.sqlite3', role_ids=selected)
    from .personal_cli import synthetic_profile
    from .personal_service import update_preference
    evidence = dict(transport='actual WSGI request/response, no TCP listener',
                    profile_kind='synthetic', view_role_ids=selected,
                    catalogue=catalogue.coverage, checks={})
    def request(method, path, body=None, token=''):
        code, value = wsgi_request(app, method, path, body, token)
        if code != 200:
            raise ValueError(f'{method} {path}: {code}: {value}')
        return value
    session = request('POST', '/api/session')
    token = session['token']  # local capability; deliberately excluded from evidence
    profile = request('PUT', '/api/profile', dict(profile=synthetic_profile('fresh_graduate'),
                                                 expected_version=None), token)
    context = request('GET', '/api/career-context', token=token)
    assert context['recommendation']['candidate_ids'] == selected
    assert all(o['personal_score'] is None for o in context['recommendation']['options'])
    assert 'internal_index' not in json.dumps(context)
    evidence['checks']['saved_profile_to_real_source_candidates'] = 'passed'
    evidence['checks']['public_market_matrix_exclusion'] = 'passed'
    evidence['context'] = context
    feedback = update_preference(profile, entity_type='role', entity_id=selected[0],
                                 state='not_interested', authorizing_request_id='synthetic-explicit-api-edit',
                                 expected_profile_version=profile['version'])
    marked = request('PUT', '/api/profile', dict(profile=feedback, expected_version=profile['version']), token)
    restarted, _ = application(output / 'runtime.sqlite3', role_ids=selected)
    assert request('GET', '/api/profile', token=token)['preferences'] == marked['preferences']
    assert wsgi_request(restarted, 'GET', '/api/profile', token=token)[1]['preferences'] == marked['preferences']
    evidence['checks']['explicit_preference_persisted_across_restart'] = 'passed'
    after = request('GET', '/api/career-context', token=token)
    assert after['recommendation']['candidate_ids'] == selected
    evidence['checks']['negative_feedback_preserves_candidates'] = 'passed'
    chat = request('POST', '/api/chat', dict(message='Explain these roles and the next-quarter evidence.',
                                           expected_profile_version=marked['version']), token)
    evidence['chat'] = chat
    evidence['checks']['actual_chat_boundary_with_provider_availability'] = chat['provider']['status']
    evidence['limitations'] = ['No live-provider success implied by bounded unavailable response.',
                               'B market service not yet connected.',
                               'N01 pending: zero numeric role-fit scores.',
                               'Local WSGI evidence is not a deployed or TCP HTTP check.']
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(dict(checks=evidence['checks'], provider=chat['provider'],
                         candidate_count=len(selected), numeric_scores=0), indent=2))
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('smoke')
    check.add_argument('--output', type=Path, required=True)
    sub.add_parser('serve')
    args = parser.parse_args()
    if args.command == 'smoke':
        smoke(args.output)
    else:
        from wsgiref.simple_server import make_server
        path = os.environ.get('MINDER_DB_PATH', str(ROOT / 'ml/artifacts/session-a/runtime/dev.sqlite3'))
        app, _ = application(path)
        with make_server('127.0.0.1', int(os.environ.get('MINDER_API_PORT', '8101')), app) as server:
            server.serve_forever()


if __name__ == '__main__':
    main()
