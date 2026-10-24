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


def a_provider_config():
    """Shared secure loader, refusing another lane's private configuration."""
    selected = os.environ.get('MINDER_GROQ_SECRET_FILE')
    if selected:
        path = Path(selected).resolve()
        for lane in ('session-b', 'session-c'):
            if path.is_relative_to(ROOT.parent / lane):
                raise ValueError('A_provider_configuration_must_not_use_another_lane')
    from minder_app.config import load_provider_config
    return load_provider_config()


def a_provider():
    """Use only A's verified model metadata; no inherited sibling artifact path."""
    from minder_app.provider_access import selected_model
    from minder_app.model_gateway import CoordinatedGroq
    config = a_provider_config()
    provider = CoordinatedGroq(key=config.api_key, model=config.model or selected_model(
        ROOT / 'ml/artifacts/session-a/runtime/groq-model-selection.json'))
    provider.daily_limit = config.daily_limit
    return provider


def application(database, *, role_ids=None, namespace='session-a', provider=None, durable_root=None):
    # C's stdlib package lives in its owned app path in THIS worktree.
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.api import Application
    from minder_app.store import Store
    from .app_context import CareerServices
    from .market_service import MarketEvidenceService
    database = Path(database).resolve()
    if namespace not in ('session-a', 'session-d', 'session-e', 'session-f'):
        raise ValueError('unknown integration namespace')
    allowed = (ROOT / 'ml/artifacts' / namespace).resolve()
    if durable_root is not None:
        # Hosting uses an explicitly configured mounted root, never HTTP input.
        configured = os.environ.get('MINDER_DATA_ROOT')
        selected = Path(durable_root).resolve()
        if (os.environ.get('MINDER_ENV') != 'production' or not configured
                or selected != Path(configured).resolve() or not selected.is_dir()
                or selected == Path('/') or selected.is_relative_to(ROOT.resolve())):
            raise ValueError('explicit_production_durable_root_required')
        allowed = selected
    if not database.is_relative_to(allowed):
        raise ValueError('integration DB must be isolated under Session A artifacts' if namespace == 'session-a'
                         else 'integration DB must stay under its declared product lane artifacts')
    store = Store(database, volume_root=allowed) if durable_root is not None else Store(database)
    return application_for_store(store, role_ids=role_ids, provider=provider)


def application_for_store(store, *, role_ids=None, provider=None):
    """Trusted server composition hook. D owns all SQL/storage semantics."""
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.api import Application
    from .app_context import CareerServices
    from .market_service import MarketEvidenceService
    catalogue = OccupationalCatalogue()
    roles = catalogue.roles() if role_ids is None else [catalogue.role(rid) for rid in role_ids]
    market = MarketEvidenceService(aliases={'role': role_aliases(catalogue), 'skill': {}})
    market_source = dict(source_id='bosch-smartrecruiters-my',
                         version='derived-snapshot-v1:' + market.version,
                         sha256=market.version,
                         uri='https://www.bosch.com.my/careers/', geography='MY',
                         available_at=market.snapshot.get('available_at', market.snapshot['collected_at']), evidence_type='source-derived')
    services = CareerServices(PersonalMatchingService(market), market, roles=roles,
                              sources=catalogue.coverage['sources'] + [market_source],
                              skill_entity_ids=[s['source_skill_id'] for s in market.mapping['skills']],
                              mode='local_source_services')
    services.role_reference = catalogue.reference
    app = Application(store, services, provider if provider is not None else a_provider())
    from minder_app.web_search import SearchRetrieval
    app.public_retrieval = SearchRetrieval()
    return app, catalogue


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
                               'This unanchored demonstration has zero assessed roles; structured evidence enables provisional scoring.',
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
    evidence['limitations'] = ['Legacy/unanchored synthetic claims do not supply the new anchored rubric.',
        'No empirical personal-fit/forecast accuracy, live Groq success or deployed scheduler claimed.',
        'Company-specific requirements unavailable; generic occupational assessment remains separate.',
        'Agent temporal/event simulations covered in C tests; this HTTP run exercises persisted proposal/actions.',
        'Model incompatibility guarded in A2 tests; no production model load is attempted here.']
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence['checks'], indent=2))
    return evidence


def provisional_demo_profile(audience='fresh_graduate', levels=(2, 4, 4)):
    """Fictional explicit source-anchored intake; never an independent label."""
    import copy
    from .personal_cli import synthetic_profile
    from .role_fit import reference
    profile = synthetic_profile(audience)
    source = copy.deepcopy(profile['evidence'][0]['provenance'])
    source['evidence_type'] = 'synthetic-fixture'
    profile.update(evidence=[], preferences=[], constraints=[])
    for i, (sid, level) in enumerate(zip(sorted(reference()['skills']), levels)):
        profile['evidence'].append(dict(evidence_id='demo-anchored-' + str(i), subject_id=sid,
            value=level, unit='onet:LV', state='known', method_id='minder-anchored-evidence-v1',
            provenance=source, assessment=dict(kind='self_report',
                statement='Fictional study-project activity supporting the selected source anchor; no paid work claimed.',
                rubric_version='onet31-essential-anchors-v1')))
    return profile


def recommendation_acceptance(output):
    """Required recommendation cases through real isolated HTTP and real A/B data."""
    import copy
    from .role_fit import RoleFitService
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('recommendation evidence must stay under A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    app, catalogue = application(output / 'runtime.sqlite3')
    report = dict(transport='actual loopback HTTP / isolated SQLite / sourced A+B services',
                  synthetic_profiles=True, cases={}, checks={}, catalogue=catalogue.coverage)
    rid = 'onet:15-1252.00'
    with http_boundary(app) as http:
        def request(method, path, body=None, token=''):
            status, value = http(method, path, body, token)
            if status != 200:
                raise ValueError('recommendation acceptance HTTP failure: ' + path + ' ' + str(status))
            return value
        def save_new(profile):
            token = request('POST', '/api/session')['token']
            profile = request('PUT', '/api/profile', dict(profile=profile, expected_version=None), token)
            return token, profile
        def context(token, selected=None):
            return request('POST', '/api/career-context', {} if selected is None else dict(selected_role_ids=selected), token)
        def summarize(ctx):
            r = ctx['recommendation']
            return dict(coverage=r['coverage'], status=r['status'], overall_ranking_complete=r['overall_ranking_complete'],
                groups=[dict(group_id=g['group_id'], basis=g['basis'], count=len(g['role_ids']),
                    top_role_ids=g['role_ids'][:3], limitation=g['limitation']) for g in r['ranking_groups']],
                targeted_questions=r['targeted_questions'])
        token, profile = save_new(provisional_demo_profile())
        reference = request('GET', '/api/assessment-reference', token=token)
        assert len(reference['skills']) == 10
        before = context(token); report['cases']['fresh_graduate'] = summarize(before)
        assert before['recommendation']['coverage']['assessed'] > 0
        assert len(before['recommendation']['candidate_ids']) == catalogue.coverage['eligible_roles']
        selected_before = context(token, [rid])
        before_score = selected_before['recommendation']['options'][0]['personal_score']
        direct = dict(request=dict(kind='update_profile', target_id=profile['profile_id'], expected=profile['version'],
            diff=[dict(path='/preferences/role/' + rid, before=None, after='not_interested')],
            reason='Synthetic explicit Not interested demonstration'), idempotency_key='demo-not-interested')
        action = request('POST', '/api/direct-action', direct, token)
        assert request('POST', '/api/direct-action', direct, token) == action
        marked = request('GET', '/api/profile', token=token)
        after = context(token, [rid]); after_score = after['recommendation']['options'][0]['personal_score']
        assert abs(before_score - after_score - 5) < 1e-6
        assert marked['evidence'] == profile['evidence']
        assert selected_before['assessment_details'][0]['gaps'] == after['assessment_details'][0]['gaps']
        def market_facts(ctx):
            return [{k: s.get(k) for k in ('kind','status','text','period','sources','source_universe_id')}
                for s in ctx['statements'] if s.get('kind') in ('current','forecast')]
        assert market_facts(selected_before) == market_facts(after)
        reset = dict(request=dict(kind='update_profile', target_id=marked['profile_id'], expected=marked['version'],
            diff=[dict(path='/preferences/role/' + rid, before='not_interested', after=None)],
            reason='Synthetic explicit preference reset'), idempotency_key='demo-reset')
        request('POST', '/api/direct-action', reset, token)
        restored = context(token, [rid])
        assert restored['recommendation']['options'][0]['personal_score'] == before_score
        assert request('GET', '/api/profile', token=token)['evidence'] == profile['evidence']
        report['cases']['not_interested_and_reset'] = dict(before=before_score, not_interested=after_score,
            reset=before_score, repeated_request_idempotent=True, skill_and_market_unchanged=True)
        switcher = provisional_demo_profile('career_switcher', (4, 4, 4, 2))
        software = catalogue.role(rid); iid = software['industry_mappings'][0]['target_id']
        method = 'minder-transferable-background-v1'
        e = copy.deepcopy(switcher['evidence'][0]); e.update(evidence_id='demo-background', subject_id=iid,
            unit='fraction_0_1', value=1, method_id=method, assessment=dict(kind='transferable_background',
                statement='Fictional sustained hands-on domain work in this industry, independently of skill ratings.', rubric_version=method))
        switcher['evidence'].append(e)
        switcher['current_fields'] = [dict(field_id=iid, field_type='industry', state='want_to_leave', evidence_ids=[e['evidence_id']])]
        switcher['preferences'] = [dict(entity_type='industry', entity_id=iid, state='not_interested', authorizing_request_id='demo-industry-request')]
        st, sp = save_new(switcher); sc = context(st)
        report['cases']['career_switcher'] = summarize(sc)
        assert set(sc['recommendation']['candidate_ids']) == set(before['recommendation']['candidate_ids'])
        report['cases']['career_switcher']['software_industry_trace'] = context(st, [rid])['assessment_details'][0]['industry_contributions']
        incomplete = provisional_demo_profile('incomplete', (2,))
        it, ip = save_new(incomplete); ic = context(it)
        assert ic['recommendation']['coverage']['assessed'] == 0 and ic['recommendation']['targeted_questions']
        report['cases']['incomplete_profile'] = summarize(ic)
        provider = request('POST', '/api/chat', dict(message='Explain my source-backed assessment and current versus next-quarter evidence.',
            expected_profile_version=request('GET','/api/profile',token=token)['version'], selected_role_ids=[rid]), token)
        report['provider'] = dict(status=provider['provider']['status'], actual_request_success=provider['provider']['status']=='available')
        report['checks']['actual_HTTP_intake_assessment_feedback_reset_market_and_provider_boundary'] = 'passed'
        assert 'internal_index' not in json.dumps(before)
    # Explicit counterfactual counts test sensitivity, never replaces factual B observations.
    market = app.services.market
    class Counterfactual:
        snapshot = market.snapshot
        favored = None
        def current(self, kind, entity_id, *, as_of):
            r = market.current(kind, entity_id, as_of=as_of)
            r['value'] = self.snapshot['collection']['accepted_ads'] if entity_id == self.favored else 0
            return r
        def forecast(self, *args, **kwargs):
            raise ValueError('unavailable_forecast_does_not_block_current')
    roles = [catalogue.role(x) for x in (rid, 'onet:15-2051.00')]
    cf = Counterfactual(); outputs=[]
    for favorite in (rid, 'onet:15-2051.00'):
        cf.favored = favorite
        r = RoleFitService(cf).assess(provisional_demo_profile(levels=(6,6,6)), roles)
        assert r['public']['ranking_groups'][0]['role_ids'][0] == favorite
        outputs.append(dict(favored=favorite, ordered=r['public']['ranking_groups'][0]['role_ids'],
                            calculation=r['internal'].get('recommendation_traces', r['internal']['market_comparison'])))
        assert outputs[-1]['calculation'], 'sensitivity evidence requires actual current-policy calculation traces'
    report['counterfactual_market_sensitivity'] = dict(kind='fictional counterfactual values; not current observations',
        same_personal_evidence=True, forecasts_unavailable=True, results=outputs)
    report['checks']['compatible_current_evidence_reverses_order_without_forecasts'] = 'passed'
    report['limitations'] = ['Policy outputs and demonstrations are provisional, not independently evaluated personal-fit labels.',
        'Employer and declared published-category comparisons remain independently scoped; most roles remain personal-only with context where available.',
        'No invented forecasts, replacement probabilities, deployment, paid execution or private profile data.']
    (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(cases={k:v.get('coverage',v) for k,v in report['cases'].items()},
                         checks=report['checks'], provider=report['provider']), indent=2))
    return report


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


def verify_web(output, playwright_module, browsers_path, *, require_live_provider=False, privacy_only=False):
    """Replay committed C acceptance against A, without editing owner modules.

    Only test ports, output paths and report port labels are adapted. Generated
    replay scripts/logs/screenshots stay in A artifacts; application code and
    test operations stay unchanged. No browser/network/provider mocking.
    """
    require_live_provider = require_live_provider or privacy_only
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
    source['http'] = source['http'].replace('full_actual_catalogue_unranked_pending_N01',
                                            'full_actual_catalogue_unranked_without_anchored_evidence')
    # Preserve C's strict DB guard. Invoke the same shared worker through A's
    # independently guarded namespace adapter instead of opening C's database.
    source['http'] = source['http'].replace('"minder_app.worker","--once",',
                                            '"minder_ml.intelligence.integration_cli","worker-once",')
    source['browser'] = source['browser'].replace("'minder_app.worker','--once',",
                                                  "'minder_ml.intelligence.integration_cli','worker-once',")
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
    privacy_original = ROOT / 'apps/frontend-web/tests/grounding_privacy_acceptance.cjs'
    privacy_script = None
    if require_live_provider:
        privacy_source = privacy_original.read_text().replace('8103','8101').replace('9103','9101')
        profile_path = output / 'grounding-profile.synthetic.json'
        profile_path.write_text(json.dumps(provisional_demo_profile()) + '\n')
        privacy_source = privacy_source.replace('ml/artifacts/session-c/grounding-profile.synthetic.json', str(profile_path))
        privacy_source = privacy_source.replace(old_browser, 'path.resolve(' + json.dumps(str(output)) + ')')
        privacy_script = output / 'replay_grounding_privacy.cjs'
        privacy_script.write_text(privacy_source)
    env = dict(os.environ, MINDER_DB_PATH=str(database), MINDER_API_PORT='8101', MINDER_UI_PORT='9101',
               PYTHONPATH=str(ROOT / 'ml/src') + os.pathsep + str(ROOT / 'apps/backend-api'),
               MINDER_PYTHON=sys.executable, MINDER_PLAYWRIGHT_MODULE=str(Path(playwright_module).resolve()),
               PLAYWRIGHT_BROWSERS_PATH=str(Path(browsers_path).resolve()))
    env['MINDER_REQUIRE_LIVE_PROVIDER'] = '1' if require_live_provider else '0'
    report = dict(implementation='Integrated application; C acceptance adapted for A ports, paths, worker namespace and current policy labels',
                  database=str(database.relative_to(ROOT)), api_port=8101, ui_port=9101,
                  owner_script_sha256={kind: hashlib.sha256(path.read_bytes()).hexdigest()
                                       for kind, path in originals.items()},
                  test_namespace_replacements=replacement_counts, checks={},
                  catalogue_references=catalogue.coverage['runtime_roles'],
                  numeric_policy='Delegated v3 provisional; anchored minimum and scoped current-market ordering')
    from .role_fit import MARKET_POLICY
    report['market_policy'] = MARKET_POLICY
    report['acceptance_scope'] = 'real_provider_privacy_only' if privacy_only else 'full_HTTP_Chromium'
    report['real_provider_required'] = require_live_provider
    report['privacy_frontend'] = 'prepared_requires_real_A_access' if not require_live_provider else 'required_live_check'
    try:
        with reserved_web_servers(app):
            commands = [('http', [sys.executable, str(http_script)]),
                                  ('browser', ['node', str(browser_script)]),
                                  ('recommendation', ['node', str(ROOT / 'docs/execution/parallel/A/checks/recommendation_browser.cjs')])]
            if privacy_only:
                commands = []
            if privacy_script:
                commands.append(('grounding_privacy', ['node', str(privacy_script)]))
                report['privacy_owner_script_sha256'] = hashlib.sha256(privacy_original.read_bytes()).hexdigest()
            for name, command in commands:
                env['MINDER_RECOMMENDATION_EVIDENCE'] = str(output / 'recommendation-browser.json')
                with (output / (name + '.log')).open('w') as log:
                    run = subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                                         stderr=subprocess.STDOUT, timeout=300)
                report['checks'][name] = dict(exit_code=run.returncode)
                if run.returncode != 0:
                    raise ValueError(name + ' acceptance failed; inspect isolated A log')
            for name in ('http', 'browser'):
                if name not in report['checks']:
                    continue
                report['checks'][name]['evidence'] = json.loads(
                    (output / ('c4.1-' + name + '-evidence.json')).read_text())
    finally:
        (output / 'integration-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return report


def verify_evidence_http(output):
    """Replay C's exact CL3 operations with A namespace/verified model binding."""
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('HTTP evidence must stay under A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    database = output / 'runtime.sqlite3'
    app, _ = application(database)
    original = ROOT / 'apps/backend-api/tests/live_evidence_bridge.py'
    source = original.read_text()
    target = "ROOT/'ml/artifacts/session-c/live-evidence-bridge.json'"
    model_check = "=='openai/gpt-oss-20b'"
    worker = "'minder_app.worker','--once',"
    if source.count(target) != 1 or source.count(model_check) != 1 or source.count(worker) != 1:
        raise ValueError('C typed HTTP acceptance changed; review A namespace adapter')
    source = source.replace('9103', '9101').replace(worker,
        "'minder_ml.intelligence.integration_cli','worker-once',")
    source = source.replace(target, 'Path(' + repr(str(output / 'live-evidence-bridge.json')) + ')')
    # Retain exact model-identity validation, using A's actual verified selection.
    # No provider-success, native-argument or source-meaning assertion is removed.
    source = source.replace(model_check, '==' + repr(app.provider.model))
    script = output / 'replay_typed_http.py'
    script.write_text('exec(compile(' + repr(source) + ', ' + repr(str(original)) +
        ', "exec"), {"__file__": ' + repr(str(original)) + ', "__name__": "__main__"})\n')
    env = dict(os.environ, MINDER_DB_PATH=str(database), MINDER_API_PORT='8101', MINDER_UI_PORT='9101',
        MINDER_ARTIFACT_DIR=str(ROOT / 'ml/artifacts/session-a'),
        PYTHONPATH=str(ROOT / 'ml/src') + os.pathsep + str(ROOT / 'apps/backend-api'))
    with reserved_web_servers(app), (output / 'typed-http.log').open('w') as log:
        run = subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env,
            stdout=log, stderr=subprocess.STDOUT, timeout=180)
    evidence = json.loads((output / 'live-evidence-bridge.json').read_text())
    report = dict(scope='C CL3 actual TCP HTTP, real A provider, source services and worker; synthetic user',
        owner_script_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
        namespace_changes=['A port/output/worker namespace', 'strict expected model equals A verified selection'],
        expected_provider_model=app.provider.model, exit_code=run.returncode, evidence=evidence,
        deployment_verified=False)
    (output / 'integration-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if run.returncode != 0 or not evidence['checks'].get('all_checks_passed'):
        raise ValueError('real typed HTTP acceptance failed; preserve evidence')
    return report


def worker_run(owner, *, once=True, poll_seconds=1, max_seconds=180):
    """A DB guard plus C's actual owner-scoped worker; no injected clock/event."""
    import time
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.agents import Worker
    path = Path(os.environ['MINDER_DB_PATH']).resolve()
    if not path.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('A worker adapter database must stay under A artifacts')
    if not owner:
        raise ValueError('explicit single-owner worker scope required')
    app, _ = application(path)
    worker = Worker(app.store, app.actions, provider=app.provider, services=app.services)
    deadline = time.monotonic() + min(300, max(1, max_seconds))
    while True:
        result = worker.tick(owner=owner)
        print(json.dumps(result), flush=True)
        if once or time.monotonic() >= deadline:
            return
        time.sleep(max(1, min(30, poll_seconds)))


def verify_typed_live(app):
    """One real provider call plus persisted actual-clock notice source checks.

    WSGI exercises the same real app/provider; the reused C acceptance separately
    verifies TCP transport and an actual upcoming-minute worker event. Never
    export the synthetic session token, raw prompt, response or ledger.
    """
    from .market_evidence import KINDS
    role = next(r for r in app.services.roles if r['role_id'] == 'onet:15-1252.00')
    expected = app.services.personal.evidence_for(role)['passages']
    for payload in expected:
        app.services.personal.verify_evidence_passage(role, payload)

    def reconcile(statements):
        covered = set()
        for claim in statements:
            if claim.get('kind') != 'market_evidence' or claim.get('status') != 'available':
                continue
            matching = [p for p in expected if p['canonical_passage'] == claim['text']
                        and p['record']['measurement_type'] == claim['measurement_type']]
            if not matching:
                raise ValueError('typed_live_canonical_source_mismatch')
            row = matching[0]['record']
            if claim['sources'] != [row['source']]:
                raise ValueError('typed_live_citation_mismatch')
            for field, actual in (('period', row['observation_period']), ('published_at', row['published_at']),
                                  ('mapping', row['mapping']), ('unit', row['unit']), ('geography', row['geography'])):
                if claim[field] != actual:
                    raise ValueError('typed_live_scope_mismatch')
            covered.add(claim['measurement_type'])
        return sorted(covered)

    token = wsgi_request(app, 'POST', '/api/session', {})[1]['token']
    code, profile = wsgi_request(app, 'PUT', '/api/profile',
        dict(profile=provisional_demo_profile(), expected_version=None), token)
    if code != 200:
        raise ValueError('typed_live_profile_failed')
    code, reply = wsgi_request(app, 'POST', '/api/chat', dict(
        message='Explain published occupation-category offerings, related MyCOL shortage-group context and broader sector context for Software Developers. Preserve scope and dates; keep employer observations and unavailable next-quarter forecasts separate.',
        expected_profile_version=profile['version'], selected_role_ids=[role['role_id']]), token)
    if (code != 200 or reply['provider']['status'] != 'available'
            or not reply['provider'].get('tool_call', {}).get('arguments_validated')
            or reply['action_status'] != 'no_mutation_requested_or_executed'):
        raise ValueError('typed_live_provider_or_authority_failed')
    chat_types = reconcile(reply['statements'])
    if not set(chat_types) - {'employer_observation'}:
        raise ValueError('typed_live_non_Bosch_fact_missing')
    if wsgi_request(app, 'GET', '/api/profile', token=token)[1] != profile:
        raise ValueError('typed_live_profile_changed')
    forecasts = [c for c in reply['statements'] if c.get('kind') == 'forecast']
    if not forecasts or any(c['status'] != 'unavailable' for c in forecasts):
        raise ValueError('typed_live_forecast_not_unavailable')
    with app.store.connect() as db:
        notices = [json.loads(r[0]) for r in db.execute('SELECT body FROM notices')]
    daily = [n for n in notices if n['event_id'].startswith('daily:')
             and n['provider_status'] == 'available_candidate_selection']
    if not daily or not any(set(reconcile(n.get('statements', []))) == set(KINDS) for n in daily):
        raise ValueError('typed_live_scheduled_source_families_missing')
    return dict(app_new_types_grounded=True, scheduled_all_four_types_grounded=True,
                app_measurement_types=chat_types, scheduled_measurement_types=list(KINDS),
                citations_periods_units_scopes_recomputed=True, profile_unchanged=True,
                forecast_unavailable=True, raw_payload_exported=False)


def verify_live(output, *, require_typed_evidence=False):
    """Real A provider/app/scheduled-event acceptance; public flags only.

    Current user authorizes these bounded calls. A's own private access is a
    required input; no C configuration/model metadata/DB is copied or imported.
    """
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.provider_access import verify
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'ml/artifacts/session-a').resolve()):
        raise ValueError('live evidence must stay under A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    report = dict(phase_id='I4.2', status='access_unavailable', checks={},
                  scope='A own private configuration, reserved ports and isolated synthetic SQLite',
                  real_provider_success=False, deployment_verified=False)
    report['typed_evidence_required'] = require_typed_evidence
    try:
        config = a_provider_config()
        report['configuration_presence'] = config.presence()
        if not config.api_key:
            report['blocker'] = 'A_authorized_private_provider_key_not_configured'
            return report
        # No key/model values/provider response bodies enter the report or logs.
        selection = ROOT / 'ml/artifacts/session-a/runtime/groq-model-selection.json'
        report['access'] = verify(config, path=selection)
        if not all(report['access'].values()):
            report['blocker'] = 'A_real_provider_access_or_native_function_check_failed'
            return report
        database = output / 'runtime.sqlite3'
        app, _ = application(database)
        original = ROOT / 'apps/backend-api/tests/live_provider_acceptance.py'
        source = original.read_text().replace('9103', '9101')
        source = source.replace('"minder_app.worker","--once",',
                                '"minder_ml.intelligence.integration_cli","worker-once",')
        source = source.replace('"minder_app.worker","--owner",',
                                '"minder_ml.intelligence.integration_cli","worker","--owner",')
        target = 'ROOT / "ml/artifacts/session-c/live-provider-acceptance.json"'
        if source.count(target) != 1:
            raise ValueError('C live acceptance changed; review A namespace adapter')
        source = source.replace(target, 'Path(' + repr(str(output / 'live-checks.json')) + ')')
        checkpoint = 'checks["app_chat_request_success"] = reply["provider"]["status"] == "available"'
        if source.count(checkpoint) != 1:
            raise ValueError('C live chat checkpoint changed; review safe diagnostic adapter')
        source = source.replace(checkpoint, checkpoint + '\n        Path(' +
            repr(str(output / 'provider-public-diagnostic.json')) +
            ').write_text(json.dumps(dict(status=reply["provider"]["status"], '
            'code=reply["provider"].get("code"), arguments_validated='
            'reply["provider"].get("tool_call",{}).get("arguments_validated") is True)))')
        script = output / 'replay_live.py'
        script.write_text('exec(compile(' + repr(source) + ', ' + repr(str(original))
            + ', "exec"), {"__file__": ' + repr(str(original)) + ', "__name__": "__main__"})\n')
        report['owner_script_sha256'] = hashlib.sha256(original.read_bytes()).hexdigest()
        env = dict(os.environ, MINDER_DB_PATH=str(database), MINDER_API_PORT='8101', MINDER_UI_PORT='9101',
            MINDER_ARTIFACT_DIR=str(ROOT / 'ml/artifacts/session-a'),
            PYTHONPATH=str(ROOT / 'ml/src') + os.pathsep + str(ROOT / 'apps/backend-api'))
        with reserved_web_servers(app), (output / 'live.log').open('w') as log:
            process = subprocess.run([sys.executable, str(script), '--configuration-confirmed'],
                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=240)
        report['checks'] = json.loads((output / 'live-checks.json').read_text())
        diagnostic = output / 'provider-public-diagnostic.json'
        if diagnostic.exists():
            report['provider_public_diagnostic'] = json.loads(diagnostic.read_text())
        if require_typed_evidence:
            try:
                if process.returncode != 0:
                    raise ValueError('original_live_prerequisite_failed')
                report['typed_evidence'] = verify_typed_live(app)
                report['checks'].update(app_new_types_grounded=True, scheduled_all_four_types_grounded=True)
            except (ValueError, KeyError, TypeError, AssertionError) as error:
                code = str(error)
                report['typed_evidence'] = dict(status='failed_no_payload_logged',
                    code=code if code.startswith('typed_live_') else 'typed_live_check_failed')
                report['checks'].update(app_new_types_grounded=False, scheduled_all_four_types_grounded=False)
        report['real_provider_success'] = process.returncode == 0 and all(report['checks'].values())
        report['status'] = 'passed_local_real_provider_and_scheduled_event' if report['real_provider_success'] else 'failed_check'
        return report
    finally:
        (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


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
    web.add_argument('--require-live-provider', action='store_true')
    web.add_argument('--privacy-only', action='store_true', help='Run only committed real-provider privacy browser; implies live provider required')
    typed_http = sub.add_parser('verify-evidence-http')
    typed_http.add_argument('--output', type=Path, required=True)
    sub.add_parser('serve')
    recommendation = sub.add_parser('verify-recommendations')
    recommendation.add_argument('--output', type=Path, required=True)
    worker = sub.add_parser('worker-once')
    worker.add_argument('--owner', required=True)
    continuous = sub.add_parser('worker')
    continuous.add_argument('--owner', required=True)
    continuous.add_argument('--poll-seconds', type=int, default=1)
    continuous.add_argument('--max-seconds', type=int, default=180)
    live = sub.add_parser('verify-live')
    live.add_argument('--output', type=Path, required=True)
    live.add_argument('--require-typed-evidence', action='store_true')
    sub.add_parser('serve-web')
    args = parser.parse_args()
    if args.command == 'verify-evidence-http':
        verify_evidence_http(args.output)
        return
    if args.command == 'verify-recommendations':
        recommendation_acceptance(args.output)
        return
    if args.command == 'worker-once':
        worker_run(args.owner)
        return
    if args.command == 'worker':
        worker_run(args.owner, once=False, poll_seconds=args.poll_seconds, max_seconds=args.max_seconds)
        return
    if args.command == 'verify-live':
        report = verify_live(args.output, require_typed_evidence=args.require_typed_evidence)
        if not report['real_provider_success']:
            raise SystemExit(1)
        return
    if args.command == 'smoke':
        smoke(args.output)
    elif args.command == 'acceptance':
        acceptance(args.output)
    elif args.command == 'verify-web':
        verify_web(args.output, args.playwright_module, args.browsers_path,
                   require_live_provider=args.require_live_provider, privacy_only=args.privacy_only)
    elif args.command == 'serve-web':
        import threading
        path = os.environ.get('MINDER_DB_PATH', str(ROOT / 'ml/artifacts/session-a/runtime/dev.sqlite3'))
        app, _ = application(path)
        with reserved_web_servers(app):
            print('Minder Session A: API 8101, UI 9101; local source services, provisional evidence-fit with partial market coverage.', flush=True)
            threading.Event().wait()
    else:
        from wsgiref.simple_server import make_server
        path = os.environ.get('MINDER_DB_PATH', str(ROOT / 'ml/artifacts/session-a/runtime/dev.sqlite3'))
        app, _ = application(path)
        with make_server('127.0.0.1', int(os.environ.get('MINDER_API_PORT', '8101')), app) as server:
            server.serve_forever()


if __name__ == '__main__':
    main()
