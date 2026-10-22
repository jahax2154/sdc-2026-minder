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
from contextlib import contextmanager
import subprocess

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
    from .market_service import MarketEvidenceService
    database = Path(database).resolve()
    if not database.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('integration DB must be isolated under Session A artifacts')
    catalogue = OccupationalCatalogue()
    roles = catalogue.roles() if role_ids is None else [catalogue.role(rid) for rid in role_ids]
    market = MarketEvidenceService(aliases={'role': role_aliases(catalogue), 'skill': {}})
    snapshot_path = ROOT / 'ml/data/market/snapshot.v1.json'
    market_source = dict(source_id='bosch-smartrecruiters-my',
                         version='derived-snapshot-v1:' + market.version,
                         sha256=hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
                         uri='https://www.bosch.com.my/careers/', geography='MY',
                         available_at=market.snapshot['collected_at'], evidence_type='source-derived')
    services = CareerServices(PersonalMatchingService(), market, roles=roles,
                              sources=catalogue.coverage['sources'] + [market_source],
                              skill_entity_ids=[s['source_skill_id'] for s in market.mapping['skills']],
                              mode='local_source_services')
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
    selection = dict(selected_role_ids=selected, selected_skill_ids=['source-term:sql'])
    context = request('POST', '/api/career-context', selection, token)
    assert context['recommendation']['candidate_ids'] == selected
    assert all(o['personal_score'] is None for o in context['recommendation']['options'])
    assert 'internal_index' not in json.dumps(context)
    evidence['checks']['saved_profile_to_real_source_candidates'] = 'passed'
    evidence['checks']['public_market_matrix_exclusion'] = 'passed'
    current = [s for s in context['statements'] if s.get('kind') == 'current']
    forecast = [s for s in context['statements'] if s.get('kind') == 'forecast']
    assert any(s['status'] == 'available' and s['sources'] for s in current)
    assert len(forecast) == 3 and all(s['status'] == 'unavailable' for s in forecast)
    evidence['checks']['actual_B_current_evidence_and_unavailable_next_quarter'] = 'passed'
    evidence['context'] = context
    feedback = update_preference(profile, entity_type='role', entity_id=selected[0],
                                 state='not_interested', authorizing_request_id='synthetic-explicit-api-edit',
                                 expected_profile_version=profile['version'])
    marked = request('PUT', '/api/profile', dict(profile=feedback, expected_version=profile['version']), token)
    restarted, _ = application(output / 'runtime.sqlite3', role_ids=selected)
    assert request('GET', '/api/profile', token=token)['preferences'] == marked['preferences']
    assert wsgi_request(restarted, 'GET', '/api/profile', token=token)[1]['preferences'] == marked['preferences']
    evidence['checks']['explicit_preference_persisted_across_restart'] = 'passed'
    after = request('POST', '/api/career-context', selection, token)
    assert after['recommendation']['candidate_ids'] == selected
    evidence['checks']['negative_feedback_preserves_candidates'] = 'passed'
    chat = request('POST', '/api/chat', dict(message='Explain these roles and the next-quarter evidence.',
                                           expected_profile_version=marked['version'], **selection), token)
    evidence['chat'] = chat
    evidence['checks']['actual_chat_boundary_with_provider_availability'] = chat['provider']['status']
    evidence['limitations'] = ['No live-provider success implied by bounded unavailable response.',
                               'B current evidence is a 39-ad inspected employer sample, not national demand.',
                               'N01 pending: zero numeric role-fit scores.',
                               'Local WSGI evidence is not a deployed or TCP HTTP check.']
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(dict(checks=evidence['checks'], provider=chat['provider'],
                         candidate_count=len(selected), numeric_scores=0), indent=2))
    return evidence


@contextmanager
def http_boundary(app):
    """Own one short-lived loopback server; no deployment or external writes."""
    from threading import Thread
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    class Quiet(WSGIRequestHandler):
        def log_message(self, *args):
            pass
    server = make_server('127.0.0.1', 0, app, handler_class=Quiet)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def request(method, path, body=None, token=''):
        raw = json.dumps(body).encode() if body is not None else None
        req = Request(f'http://127.0.0.1:{server.server_port}' + path, data=raw, method=method,
                      headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
        try:
            with urlopen(req, timeout=30) as response:
                return response.status, json.load(response)
        except HTTPError as response:
            with response:
                return response.code, json.load(response)
    try:
        yield request
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def acceptance(output):
    """Exercise persisted real-source user flows through actual local HTTP."""
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('evidence must stay in Session A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    app, catalogue = application(output / 'runtime.sqlite3')
    from .personal_cli import synthetic_profile
    evidence = dict(transport='real loopback HTTP to actual application', synthetic_profiles=True,
                    checks={}, limitations=[], examples={})
    selected = ['onet:15-1252.00', 'onet:11-1011.00']
    selection = dict(selected_role_ids=selected, selected_skill_ids=['source-term:sql'])
    with http_boundary(app) as http:
        def request(method, path, body=None, token='', expected=200):
            code, value = http(method, path, body, token)
            if code != expected:
                raise ValueError(f'{method} {path}: expected {expected}, got {code}: {value}')
            return value
        session = request('POST', '/api/session')
        token = session['token']
        profile = request('PUT', '/api/profile', dict(profile=synthetic_profile(), expected_version=None), token)
        broad = request('GET', '/api/career-context', token=token)
        assert len(broad['recommendation']['candidate_ids']) == catalogue.coverage['eligible_roles']
        assert all(o['personal_score'] is None and o['rank'] is None for o in broad['recommendation']['options'])
        evidence['checks']['student_no_industry_broad_source_candidates'] = len(broad['recommendation']['candidate_ids'])
        switcher = synthetic_profile('career_switcher')
        profile = request('PUT', '/api/profile', dict(profile=switcher, expected_version=profile['version']), token)
        current = request('POST', '/api/career-context', selection, token)
        assert set(current['recommendation']['candidate_ids']) == set(selected)
        evidence['checks']['career_switcher_cross_industry_candidates_retained'] = 'passed'
        before_evidence = profile['evidence']
        def preference(state, key):
            nonlocal profile
            prior = next((p['state'] for p in profile['preferences'] if p['entity_type'] == 'role'
                          and p['entity_id'] == selected[0]), None)
            body = dict(request=dict(kind='update_profile', target_id=profile['profile_id'],
                expected=profile['version'], diff=[dict(path='/preferences/role/' + selected[0],
                    before=prior, after=state)], reason='Explicit synthetic acceptance feedback'), idempotency_key=key)
            result = request('POST', '/api/direct-action', body, token)
            assert result == request('POST', '/api/direct-action', body, token)
            profile = result['target']
        preference('not_interested', 'acceptance-feedback')
        marked = request('POST', '/api/career-context', selection, token)
        assert set(marked['recommendation']['candidate_ids']) == set(selected)
        marked_option = next(o for o in marked['recommendation']['options'] if o['role_id'] == selected[0])
        assert 'Not interested' in marked_option['explanation']
        # Compare measured public values/dates, excluding fresh issue timestamps.
        def facts(context):
            return [(s.get('kind'), s['text'], s.get('period'), s.get('published_at'))
                    for s in context['statements'] if s.get('kind') in ('current', 'forecast')]
        assert facts(current) == facts(marked)
        preference(None, 'acceptance-feedback-reset')
        assert profile['evidence'] == before_evidence
        assert not profile['preferences']
        evidence['checks']['feedback_persisted_retry_reset_market_and_evidence_unchanged'] = 'passed'
        assert any(s.get('kind') == 'current' and s.get('status') == 'available' for s in current['statements'])
        assert all(s.get('status') == 'unavailable' for s in current['statements'] if s.get('kind') == 'forecast')
        assert 'internal_index' not in json.dumps(current)
        evidence['checks']['current_sources_and_next_quarter_unavailable_without_raw_matrix'] = 'passed'
        company = request('POST', '/api/company-explorer', dict(employer_id='bosch', role_id=selected[0]), token)
        assert company['main_recommendations_changed'] is False
        assert company['result']['status'] == 'requirements_unavailable'
        assert company['other_supported_roles']
        evidence['checks']['company_source_scope_and_generic_assessment_without_vacancy_claim'] = 'passed'
        draft = request('POST', '/api/intake', dict(text='I may know SQL; please help me clarify.', channel='chat'), token)
        assert draft['status'] == 'pending_clarification'
        assert request('GET', '/api/profile', token=token) == profile
        updated = json.loads(json.dumps(profile))
        claim = json.loads(json.dumps(updated['evidence'][0]))
        claim.update(evidence_id='acceptance-sql-claim', subject_id='source-term:sql', value='self-report, not assessed',
                     unit='claim', method_id='explicit-self-report')
        updated['evidence'].append(claim)
        profile = request('PUT', '/api/profile', dict(profile=updated, expected_version=profile['version']), token)
        assert any(e['evidence_id'] == 'acceptance-sql-claim' for e in request('GET', '/api/profile', token=token)['evidence'])
        evidence['checks']['ambiguous_chat_draft_then_explicit_profile_evidence_update'] = 'passed'
        preview = request('POST', '/api/pathway-preview', dict(role_id=selected[0]), token)
        assert preview['saved'] is False and preview['design']['activities']
        evidence['checks']['real_role_requirements_feed_unknown_effort_pathway_preview'] = 'passed'
        plan = json.loads((ROOT / 'contracts/fixtures/parallel-v1/plan_progress.json').read_text())['payload']
        plan['selected_role_id'] = selected[0]
        plan['tasks'][0]['estimated_hours'] = 1
        plan['constraints'] = [dict(constraint_id='capacity', scope='weekly_hours', hard=True,
                                    value=10, unit='hours_per_week', evidence_id='synthetic-capacity')]
        plan = request('POST', '/api/plans', dict(plan=plan, idempotency_key='acceptance-plan'), token)['plan']
        def move_request(p, after):
            return dict(kind='reschedule_task', target_id=p['plan_id'], expected=p['state_version'],
                diff=[dict(path='/tasks/synthetic-task/scheduled_at', before=p['tasks'][0]['scheduled_at'], after=after)],
                reason='Explicit synthetic user command')
        body = dict(request=move_request(plan, '2026-10-25T11:00:00Z'), idempotency_key='acceptance-move')
        moved = request('POST', '/api/direct-action', body, token)
        assert moved == request('POST', '/api/direct-action', body, token)
        assert moved['action']['approval_state'] == 'not_required_direct'
        evidence['checks']['direct_task_move_persists_once_without_approval'] = 'passed'
        plan = moved['target']
        proposed = request('POST', '/api/proposals', dict(request=move_request(plan, '2026-10-26T11:00:00Z')), token)
        assert request('GET', '/api/plans', token=token)['plans'][0] == plan
        decision = dict(proposal_id=proposed['preview']['proposal_id'], decision='reject',
                        preview_hash=proposed['preview_hash'], expected_state_version=plan['state_version'])
        request('POST', '/api/proposal-decision', decision, token)
        assert request('GET', '/api/plans', token=token)['plans'][0] == plan
        first = request('POST', '/api/proposals', dict(request=move_request(plan, '2026-10-26T11:00:00Z')), token)
        stale = request('POST', '/api/proposals', dict(request=move_request(plan, '2026-10-27T11:00:00Z')), token)
        decision.update(proposal_id=first['preview']['proposal_id'], decision='approve', preview_hash=first['preview_hash'])
        approved = request('POST', '/api/proposal-decision', decision, token)
        decision.update(proposal_id=stale['preview']['proposal_id'], preview_hash=stale['preview_hash'])
        request('POST', '/api/proposal-decision', decision, token, expected=409)
        evidence['checks']['proposal_no_mutation_reject_exact_approve_and_stale_conflict'] = 'passed'
        plan = approved['target']
        complete = dict(kind='complete_task', target_id=plan['plan_id'], expected=plan['state_version'],
            diff=[dict(path='/tasks/synthetic-task/state', before='scheduled', after='completed')],
            reason='Explicit synthetic Complete action')
        finished = request('POST', '/api/direct-action', dict(request=complete, idempotency_key='acceptance-complete'), token)
        assert finished['target']['tasks'][0]['activity_completion']
        assert not finished['target']['tasks'][0]['mastery_verified']
        request('POST', '/api/direct-action', dict(request=move_request(finished['target'], '2026-10-28T11:00:00Z'),
                                                 idempotency_key='cannot-move-completed'), token, expected=409)
        evidence['checks']['completion_preserves_mastery_distinction_and_history'] = 'passed'
        stale_profile = request('PUT', '/api/profile', dict(profile=profile, expected_version='wrong'), token, expected=409)
        chat = request('POST', '/api/chat', dict(message='Explain the source-backed outlook.',
                                                expected_profile_version=profile['version'], **selection), token)
        evidence['checks']['failed_write_is_conflict'] = stale_profile['code']
        evidence['checks']['actual_provider_state'] = chat['provider']
        evidence['examples'] = dict(context=current, company=company, chat=chat,
                                    pathway_design=preview['design'])
    evidence['limitations'] = ['N01 pending: complete synthetic evidence does not yield numeric scores.',
        'No empirical personal-fit/forecast accuracy, live Groq success or deployed scheduler claimed.',
        'Company-specific requirements unavailable; generic occupational assessment remains separate.',
        'Agent temporal/event simulations covered in C tests; this HTTP run exercises persisted proposal/actions.',
        'Model incompatibility guarded in A2 tests; no production model load is attempted here.']
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence['checks'], indent=2))
    return evidence


@contextmanager
def reserved_web_servers(app):
    """Reuse C's committed web wrapper with A's application/DB/port ownership."""
    from threading import Thread
    from wsgiref.simple_server import make_server
    from minder_app.dev import web_app, QuietHandler
    from contextlib import ExitStack
    with ExitStack() as stack:
        api = stack.enter_context(make_server('127.0.0.1', int(os.environ.get('MINDER_API_PORT', '8101')),
                                              app, handler_class=QuietHandler))
        web = stack.enter_context(make_server('127.0.0.1', int(os.environ.get('MINDER_UI_PORT', '9101')),
                                              web_app(app), handler_class=QuietHandler))
        if api.server_port != 8101 or web.server_port != 9101:
            raise ValueError('Session A integration uses reserved ports 8101/9101')
        threads = [Thread(target=s.serve_forever, daemon=True) for s in (api, web)]
        for thread in threads:
            thread.start()
        try:
            yield
        finally:
            for server in (api, web):
                server.shutdown()
            for thread in threads:
                thread.join(timeout=5)


def verify_web(output, playwright_module, browsers_path):
    """Replay committed C acceptance against A, without editing owner modules.

    Only test ports, output paths and report port labels are adapted. Generated
    replay scripts/logs/screenshots stay in A artifacts; application code and
    test operations stay unchanged. No browser/network/provider mocking.
    """
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('web evidence must stay under Session A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    database = output / 'runtime.sqlite3'
    app, catalogue = application(database)
    originals = dict(http=ROOT / 'apps/backend-api/tests/http_acceptance.py',
                     browser=ROOT / 'apps/frontend-web/tests/browser_acceptance.cjs')
    source = {kind: path.read_text() for kind, path in originals.items()}
    replacement_counts = {}
    for kind in source:
        replacement_counts[kind] = {p: source[kind].count(p) for p in ('8103', '9103')}
        source[kind] = source[kind].replace('8103', '8101').replace('9103', '9101')
    old_http = 'ROOT / "ml/artifacts/session-c/c4.1-http-evidence.json"'
    old_browser = "path.resolve('ml/artifacts/session-c')"
    if source['http'].count(old_http) != 1 or source['browser'].count(old_browser) != 1:
        raise ValueError('owner acceptance paths changed; review namespace adapter')
    source['http'] = source['http'].replace(old_http, 'Path(' + repr(str(output / 'c4.1-http-evidence.json')) + ')')
    # The original __file__ keeps the test's repository ROOT/cwd calculation.
    http_script = output / 'replay_http.py'
    http_script.write_text('exec(compile(' + repr(source['http']) + ', ' + repr(str(originals['http']))
                           + ', "exec"), {"__file__": ' + repr(str(originals['http']))
                           + ', "__name__": "__main__"})\n')
    browser_script = output / 'replay_browser.cjs'
    browser_script.write_text(source['browser'].replace(old_browser, 'path.resolve(' + json.dumps(str(output)) + ')'))
    env = dict(os.environ, MINDER_DB_PATH=str(database), MINDER_API_PORT='8101', MINDER_UI_PORT='9101',
               PYTHONPATH=str(ROOT / 'ml/src') + os.pathsep + str(ROOT / 'apps/backend-api'),
               MINDER_PYTHON=sys.executable, MINDER_PLAYWRIGHT_MODULE=str(Path(playwright_module).resolve()),
               PLAYWRIGHT_BROWSERS_PATH=str(Path(browsers_path).resolve()))
    report = dict(implementation='unchanged committed C application/UI/tests with A binding',
                  database=str(database.relative_to(ROOT)), api_port=8101, ui_port=9101,
                  owner_script_sha256={kind: hashlib.sha256(path.read_bytes()).hexdigest()
                                       for kind, path in originals.items()},
                  test_namespace_replacements=replacement_counts, checks={},
                  catalogue_references=catalogue.coverage['runtime_roles'],
                  numeric_policy='N01 pending/inactive; no numeric role ranking')
    try:
        with reserved_web_servers(app):
            for name, command in [('http', [sys.executable, str(http_script)]),
                                  ('browser', ['node', str(browser_script)])]:
                with (output / (name + '.log')).open('w') as log:
                    run = subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                                         stderr=subprocess.STDOUT, timeout=180)
                report['checks'][name] = dict(exit_code=run.returncode)
                if run.returncode != 0:
                    raise ValueError(name + ' acceptance failed; inspect isolated A log')
            for name in ('http', 'browser'):
                report['checks'][name]['evidence'] = json.loads(
                    (output / ('c4.1-' + name + '-evidence.json')).read_text())
    finally:
        (output / 'integration-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('smoke')
    check.add_argument('--output', type=Path, required=True)
    accept = sub.add_parser('acceptance')
    accept.add_argument('--output', type=Path, required=True)
    web = sub.add_parser('verify-web')
    web.add_argument('--output', type=Path, required=True)
    web.add_argument('--playwright-module', type=Path, required=True)
    web.add_argument('--browsers-path', type=Path, required=True)
    sub.add_parser('serve')
    sub.add_parser('serve-web')
    args = parser.parse_args()
    if args.command == 'smoke':
        smoke(args.output)
    elif args.command == 'acceptance':
        acceptance(args.output)
    elif args.command == 'verify-web':
        verify_web(args.output, args.playwright_module, args.browsers_path)
    elif args.command == 'serve-web':
        import threading
        path = os.environ.get('MINDER_DB_PATH', str(ROOT / 'ml/artifacts/session-a/runtime/dev.sqlite3'))
        app, _ = application(path)
        with reserved_web_servers(app):
            print('Minder Session A: API 8101, UI 9101; local source services, N01 pending.', flush=True)
            threading.Event().wait()
    else:
        from wsgiref.simple_server import make_server
        path = os.environ.get('MINDER_DB_PATH', str(ROOT / 'ml/artifacts/session-a/runtime/dev.sqlite3'))
        app, _ = application(path)
        with make_server('127.0.0.1', int(os.environ.get('MINDER_API_PORT', '8101')), app) as server:
            server.serve_forever()


if __name__ == '__main__':
    main()
