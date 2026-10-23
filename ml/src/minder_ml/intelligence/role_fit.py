"""Delegated provisional evidence-fit and scoped current-market ordering.

No occupation rating, title, interest or missing answer becomes person ability.
The old preparation scorer and original pending proposal remain separate APIs.
"""
import copy
from datetime import datetime, timezone
import json
import math

from jsonschema.exceptions import ValidationError
from .policy import ROOT, fingerprint
from .policy_sources import role_reference_v3
from .service_contracts import CONTRACT_VERSION, validate, next_calendar_quarter

POLICY_ID = 'personal-role-fit-v3-provisional'
LEGACY_MARKET_POLICY = 'personal-current-cohort-v1'
INTERMEDIATE_MARKET_POLICY = 'personal-current-evidence-v2'
MARKET_POLICY = 'personal-current-evidence-v2.1'
CONFIG = ROOT / 'ml/configs/intelligence/personal-role-fit.v3.json'


def policy():
    p = json.loads(CONFIG.read_text())
    if p['policy_id'] != POLICY_ID or p['status'] != 'delegated_provisional' or not p['active']:
        raise ValueError('replacement policy implementation is inactive/incompatible')
    return p


def reference():
    """Public intake support; sourced examples and declared evidence protocol."""
    data = role_reference_v3()
    return dict(policy_id=POLICY_ID, skill_method_id='minder-anchored-evidence-v1',
                skill_rubric_version='onet31-essential-anchors-v1',
                minimum_assessed_skills=3, minimum_coverage=.3,
                skills=data['skill_rubrics'], industries=data['industries'],
                work_styles=data['work_style_labels'], sources=list(data['sources'].values()),
                notice='Choose source activity examples and describe your evidence. Self-report/project claims are provisional, not verified competence.')


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _valid_skill(e, ref):
    a = e.get('assessment', {})
    if (e['state'] != 'known' or e['subject_id'] not in ref['skill_rubrics']
            or e['unit'] != 'onet:LV' or e['method_id'] != 'minder-anchored-evidence-v1'
            or not _number(e['value'])
            or e['value'] not in [0] + [r['value'] for r in ref['skill_rubrics'][e['subject_id']]['anchors']]
            or a.get('rubric_version') != 'onet31-essential-anchors-v1'
            or len(a.get('statement', '').strip()) < 20
            or a.get('kind') not in ('self_report', 'documented_demonstration', 'reviewed_assessment')):
        return False
    if e['provenance']['evidence_type'] not in ('explicit-user', 'synthetic-fixture', 'human-reviewed'):
        return False
    return a['kind'] != 'reviewed_assessment' or e['provenance']['evidence_type'] == 'human-reviewed'


def _optional_evidence(profile, subject, method, kind):
    rows = [e for e in profile['evidence'] if e['subject_id'] == subject and e['state'] == 'known'
            and e['method_id'] == method and e['unit'] == 'fraction_0_1' and _number(e['value'])
            and e['value'] in (0, .5, 1) and e.get('assessment', {}).get('kind') == kind
            and e.get('assessment', {}).get('rubric_version') == method
            and len(e.get('assessment', {}).get('statement', '').strip()) >= 20
            and e['provenance']['evidence_type'] in ('explicit-user', 'synthetic-fixture', 'human-reviewed')]
    if not rows or len({e['value'] for e in rows}) != 1:
        return None, []
    return rows[0]['value'], sorted({e['evidence_id'] for e in rows})


def _utility(preference):
    return {'interested': 1, 'not_interested': 0, 'neutral': .5}.get((preference or {}).get('state'))


def _assessment(profile, role, p, ref, scorer_kind):
    requirements = {e['subject_id']: e for e in role['requirements']
                    if e['unit'] == 'onet:LV' and e['state'] == 'known' and _number(e['value'])
                    and e['value'] > 0 and e['subject_id'] in ref['skill_rubrics']}
    observations = {}
    for e in profile['evidence']:
        if _valid_skill(e, ref):
            observations.setdefault(e['subject_id'], []).append(e)
    gaps, ratios, used, kinds = [], [], [], {'self_report': [], 'documented_demonstration': [], 'reviewed_assessment': []}
    for sid, requirement in sorted(requirements.items()):
        rows = observations.get(sid, [])
        ids = sorted({e['evidence_id'] for e in rows})
        if not rows or len({e['value'] for e in rows}) != 1:
            gaps.append(dict(criterion_id=sid, state='unknown', evidence_ids=ids,
                             reason='Conflicting anchored observations; clarify the current assessment.' if rows
                             else 'Missing explicit anchored skill assessment; do not infer competence.'))
            continue
        level = rows[0]['value']
        ratios.append(min(level / requirement['value'], 1.))
        used += ids
        for e in rows:
            kinds[e['assessment']['kind']].append(e['evidence_id'])
        gaps.append(dict(criterion_id=sid, state='met' if level >= requirement['value'] else 'gap', evidence_ids=ids,
                         reason=f'Declared anchored level {level} compared with occupational LV {requirement["value"]}; provisional evidence fit, not verified employment qualification.'))
    coverage = len(ratios) / len(requirements) if requirements else 0.
    minimum = len(ratios) >= p['minimum_assessed_skills'] and coverage >= p['minimum_coverage']
    c = sum(ratios) / len(ratios) if ratios else None
    prefs = {(e['entity_type'], e['entity_id']): e for e in profile['preferences']}
    industries = []
    for mapping in role['industry_mappings']:
        if mapping['status'] not in ('source_accepted', 'policy_accepted'):
            continue
        iid = mapping['target_id']
        background, ids = _optional_evidence(profile, iid, 'minder-transferable-background-v1', 'transferable_background')
        pref = prefs.get(('industry', iid)); utility = _utility(pref)
        points = p['background_points'] * (background if background is not None else 0)
        points += p['industry_interest_points'] * (2 * utility - 1) if utility is not None else 0
        industries.append(dict(industry_id=iid, background=background, preference_utility=utility,
            assessment=(points + 5) / 15 if background is not None or utility is not None else None,
            adjustment_points=points, selected_path=False, rule_id='v3-industry-context-once', evidence_ids=ids,
            preference=copy.deepcopy(pref), background_fields=[copy.deepcopy(f) for f in profile['current_fields']
                if f['field_id'] == iid and f['field_type'] == 'industry'],
            role_mapping_status='supported', missing_reasons=[] if background is not None and utility is not None
                else ['Optional missing components contribute no adjustment; raw values remain unknown.']))
    selected = max(industries, key=lambda i: (i['adjustment_points'], i['industry_id']), default=None)
    if selected:
        selected['selected_path'] = True
    background = selected['background'] if selected else None
    industry_u = selected['preference_utility'] if selected else None
    background_points = p['background_points'] * background if background is not None else 0
    industry_points = p['industry_interest_points'] * (2 * industry_u - 1) if industry_u is not None else 0
    role_pref = prefs.get(('role', role['role_id'])); role_u = _utility(role_pref)
    role_points = p['role_interest_points'] * (2 * role_u - 1) if role_u is not None else 0
    style_values, style_ids = [], []
    for mapping in role.get('work_style_mappings', []):
        if mapping['status'] not in ('source_accepted', 'policy_accepted'):
            continue
        value, ids = _optional_evidence(profile, mapping['target_id'], 'minder-work-style-preference-v1', 'work_style_preference')
        if value is not None:
            style_values.append(value); style_ids += ids
    w = sum(style_values) / len(style_values) if style_values else None
    style_points = p['work_style_points'] * (2 * w - 1) if w is not None else 0
    components = []
    for name, value, points, weight, ids in (
            ('capability', c, p['capability_points'] * c if c is not None else 0, .8, used),
            ('transferable_background', background, background_points, .05, selected['evidence_ids'] if selected else []),
            ('industry_interest', industry_u, industry_points, .05, []),
            ('role_interest', role_u, role_points, .05, []),
            ('work_style', w, style_points, .05, style_ids)):
        components.append(dict(component_id=name, value=value, weight=weight if value is not None else 0,
            contribution_points=points, unit='fraction_0_1', rule_id='v3-known-evidence-and-optional-adjustments',
            evidence_ids=sorted(set(ids)), missing_reasons=[] if value is not None else ['Unknown; no invented measurement or optional adjustment.']))
    raw = sum(v['contribution_points'] for v in components)
    score = max(0., min(100., raw)) if minimum and scorer_kind == 'baseline' else None
    status = 'scored' if score is not None else 'model_not_ready' if minimum else 'insufficient_information'
    excluded, unresolved = False, []
    for constraint in profile['constraints']:
        if constraint['hard'] and constraint['scope'] in ('role_allowlist', 'role_denylist'):
            if not isinstance(constraint['value'], str):
                raise ValueError('explicit role restriction requires JSON list text')
            ids = json.loads(constraint['value'])
            if constraint['unit'] != 'role_ids_json' or not isinstance(ids, list) or any(not isinstance(i, str) for i in ids):
                raise ValueError('explicit role restriction requires role_ids_json')
            excluded |= (role['role_id'] not in ids) if constraint['scope'] == 'role_allowlist' else (role['role_id'] in ids)
        elif constraint['scope'] not in ('weekly_hours', 'budget', 'planning_horizon'):
            unresolved.append(copy.deepcopy(constraint))
    if excluded:
        score, status = None, 'constraint_excluded'
    unknowns = [g['criterion_id'] for g in gaps if g['state'] == 'unknown']
    if not minimum:
        unknowns.append('minimum_anchored_skill_evidence_absent')
    if scorer_kind != 'baseline':
        unknowns.append('no_selected_v3_learned_model')
    questions = []
    if not minimum:
        needed = max(p['minimum_assessed_skills'], math.ceil(p['minimum_coverage'] * len(requirements))) - len(ratios)
        labels = [ref['skill_rubrics'][g['criterion_id']]['label'] for g in gaps if g['state'] == 'unknown'][:max(1, needed)]
        questions = [f'Provide an anchored activity level and evidence description for {label}.' for label in labels]
    return dict(profile_id=profile['profile_id'], profile_version=profile['version'], role_id=role['role_id'],
        role_version=role['version'], policy_version=POLICY_ID, policy_status='provisional', model_version=None,
        scorer_kind=scorer_kind, score_status=status, score=round(score, 8) if score is not None else None,
        measurement='personal_role_evidence_fit_v3', components=components, industry_contributions=industries,
        gaps=gaps, prerequisites=[], evidence_ids=sorted(set(used + style_ids + (selected['evidence_ids'] if selected else []))), unknowns=unknowns,
        targeted_questions=questions, trace_rule_ids=['N01-R1-delegated', 'v3-partial-evidence-no-imputation',
            'v3-no-industry-exclusion', 'v3-preferences-once'], role_preference=copy.deepcopy(role_pref),
        profile_fields=copy.deepcopy(profile['current_fields']), unresolved_constraints=unresolved,
        assessment_coverage=dict(assessed_count=len(ratios), required_count=len(requirements), fraction=coverage,
                                 minimum_met=minimum, minimum_count=p['minimum_assessed_skills'], minimum_fraction=p['minimum_coverage']),
        evidence_kinds={k: sorted(set(v)) for k, v in kinds.items()}, unclipped_score=raw,
        limitations=['Partial essential-skill evidence compatibility; not independently verified competence or employment qualification.',
                     'Optional absence contributes no adjustment; source context is US, not Malaysian demand.'])


class RoleFitService:
    def __init__(self, market_service=None, *, as_of=None):
        self.market_service, self.as_of = market_service, as_of
        self.ref = role_reference_v3()

    def reference(self):
        return reference()

    def _market(self, role_id, kind, stamp):
        try:
            if self.market_service is None:
                raise ValueError('market_service_not_connected')
            r = (self.market_service.current('role', role_id, as_of=stamp) if kind == 'current'
                 else self.market_service.forecast('role', role_id, issued_at=stamp))
            validate('MarketResult', r)
            if (r['entity_id'], r['entity_type'], r['kind']) != (role_id, 'role', kind):
                raise ValueError('market_entity_mismatch')
            if r['status'] == 'available':
                issue = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
                dates = [datetime.fromisoformat(r[k].replace('Z', '+00:00'))
                         for k in ('published_at', 'available_at', 'ingested_at')]
                if any(d.tzinfo is None or d > issue for d in dates) or r['observation_period']['end'] > stamp[:10]:
                    raise ValueError('market_not_available_at_issue')
            return copy.deepcopy(r)
        except (ValueError, KeyError, OSError, ValidationError):
            return dict(entity_type='role', entity_id=role_id, kind=kind, status='unavailable', geography='MY',
                source_universe_id='not_available', cohort_version='not_available', measurement='advertisements',
                unit='advertisements', denominator=None, observation_period=dict(start=stamp[:10], end=stamp[:10]),
                published_at=None, available_at=None, ingested_at=None, issued_at=stamp,
                target_period=next_calendar_quarter(stamp) if kind == 'forecast' else None,
                horizon='next_full_calendar_quarter' if kind == 'forecast' else 'observed', value=None,
                internal_index=None, uncertainty=dict(lower=None, upper=None, method=None),
                missing_reasons=[kind + '_service_unavailable_or_incompatible'], source_ids=[], model_version=None,
                explanation=kind.capitalize() + ' evidence unavailable; no value inferred.')

    def assess(self, profile, roles, *, scorer_kind='baseline', policy_version=POLICY_ID,
               market_period_policy_key=MARKET_POLICY):
        p = policy()
        if policy_version != POLICY_ID or market_period_policy_key not in (MARKET_POLICY, LEGACY_MARKET_POLICY, INTERMEDIATE_MARKET_POLICY):
            raise ValueError('explicit v3 personal/current policy required')
        if scorer_kind not in ('baseline', 'ridge', 'xgboost'):
            raise ValueError('unknown scorer_kind')
        validate('Profile', profile)
        if len({r['role_id'] for r in roles}) != len(roles):
            raise ValueError('duplicate role identity')
        stamp = self.as_of or datetime.now(timezone.utc).isoformat()
        assessments, current, forecast, candidates, options, groups, compared, traces = [], [], [], [], [], [], [], []
        for role in roles:
            validate('Role', role)
            if role['eligibility'] != 'supported':
                continue
            a = _assessment(profile, role, p, self.ref, scorer_kind)
            assessments.append(a)
            if a['score_status'] == 'constraint_excluded':
                continue
            candidates.append(role['role_id'])
            current.append(self._market(role['role_id'], 'current', stamp))
            forecast.append(self._market(role['role_id'], 'forecast', stamp))
            options.append(dict(role_id=role['role_id'], rank=None, ranking_group=None, ranking_basis='unassessed',
                personal_score=a['score'], score_status=a['score_status'], evidence_coverage=a['assessment_coverage']['fraction'],
                explanation=(f"{role['label']}: provisional essential-skill evidence fit {a['score']:.2f}/100; "
                    f"{a['assessment_coverage']['assessed_count']}/{a['assessment_coverage']['required_count']} criteria assessed. "
                    'This is evidence compatibility, not employment qualification.' if a['score'] is not None else
                    f"{role['label']}: no supported numerical assessment yet; provide at least three anchored skill assessments and 30% coverage."),
                source_ids=sorted({role['source']['source_id']} | {e['provenance']['source_id'] for e in role['requirements']}),
                unknowns=a['unknowns']))
            if (a['role_preference'] or {}).get('state') == 'not_interested':
                options[-1]['explanation'] += ' Not interested: preference contribution reduced; role retained.'
        by_id = {o['role_id']: o for o in options}
        cohort_rows = {}
        sample = getattr(self.market_service, 'snapshot', {}) or {}
        size = sample.get('collection', {}).get('accepted_ads')
        for r in current:
            if (by_id[r['entity_id']]['personal_score'] is None or r['status'] != 'available' or r['geography'] != 'MY'
                    or r['measurement'] != 'unique_valid_inspected_advertisements' or r['unit'] != 'advertisements'
                    or not _number(size) or size <= 0 or not _number(r['value']) or not 0 <= r['value'] <= size
                    or r['source_universe_id'] != sample.get('source_universe_id')):
                continue
            key = fingerprint({k: r[k] for k in ('geography', 'source_universe_id', 'cohort_version', 'measurement',
                                'unit', 'observation_period', 'denominator', 'source_ids')} | {'sample_size': size})
            cohort_rows.setdefault(key, []).append(r)
        for key, rows in sorted(cohort_rows.items()):
            if len(rows) < 2:
                continue
            gid = 'current:' + key[:16]
            scores = {}
            for r in rows:
                rid = r['entity_id']; f = by_id[rid]['personal_score']
                m = 100 * math.log1p(r['value']) / math.log1p(size)
                s = p['personal_fraction'] * f + p['current_fraction'] * m
                scores[rid] = s
                compared.append(dict(role_id=rid, score=s))
                traces.append(dict(role_id=rid, group_id=gid, personal_score=f, current_support_index=m,
                    sample_size=size, observed_count=r['value'], final_score=s, policy_id=LEGACY_MARKET_POLICY))
                by_id[rid].update(ranking_group=gid, ranking_basis='personal_and_comparable_current')
            ordered = sorted(scores, key=lambda rid: (-scores[rid], -by_id[rid]['personal_score'], rid))
            for rank, rid in enumerate(ordered, 1):
                by_id[rid]['rank'] = rank
            groups.append(dict(group_id=gid, basis='personal_and_comparable_current', role_ids=ordered,
                limitation='Within this inspected MY source cohort only; not comparable to other groups or national demand.'))
        personal = sorted((rid for rid, o in by_id.items() if o['personal_score'] is not None and o['rank'] is None),
                          key=lambda rid: (-by_id[rid]['personal_score'], rid))
        if personal:
            for rank, rid in enumerate(personal, 1):
                by_id[rid].update(rank=rank, ranking_group='personal-only', ranking_basis='personal_only_market_unsupported')
            groups.append(dict(group_id='personal-only', basis='personal_only_market_unsupported', role_ids=personal,
                limitation='Market comparison unsupported; this personal-only fallback is not full recommendation completion.'))
        ordered_ids = [rid for g in groups for rid in g['role_ids']]
        ordered_ids += sorted(rid for rid in candidates if rid not in set(ordered_ids))
        n_scored = sum(a['score'] is not None for a in assessments)
        complete = bool(candidates) and len(compared) == len(candidates) and len(groups) == 1
        coverage = dict(considered_eligible=len(assessments), candidates=len(candidates), assessed=n_scored,
            excluded=sum(a['score_status'] == 'constraint_excluded' for a in assessments),
            current_available=sum(r['status'] == 'available' for r in current),
            current_comparable_ranked=len(compared), personal_only_ranked=len(personal),
            insufficient_evidence=sum(a['score_status'] == 'insufficient_information' for a in assessments))
        result = dict(public=dict(contract_version=CONTRACT_VERSION, profile_id=profile['profile_id'],
            profile_version=profile['version'], policy_version=POLICY_ID, model_version=None,
            candidate_ids=candidates, market_period_policy_key=LEGACY_MARKET_POLICY, status='available' if complete else 'partial',
            options=[by_id[rid] for rid in ordered_ids], ranking_groups=groups, coverage=coverage,
            ordering_scope='within_groups_only', overall_ranking_complete=complete,
            targeted_questions=next((a['targeted_questions'] for a in assessments if a['targeted_questions']), []),
            limitations=['Provisional partial essential-skill evidence fit; not validated career accuracy or hiring probability.',
                'Groups have independent ranks; display group order does not compare opportunities across coverage.',
                'Current Malaysian evidence is a bounded employer sample; forecasts are separate and may be unavailable.']
                + ([] if complete else ['Partial market/evidence coverage: personal-only fallback is not full completion.'])),
            internal=dict(personal_assessments=assessments, current_market=current, forecast_market=forecast,
                combined_score_policy_version=LEGACY_MARKET_POLICY, combined_scores=compared, market_comparison=traces))
        validate('Recommendation', result)
        if market_period_policy_key != LEGACY_MARKET_POLICY:
            from .market_evidence import EvidenceContext
            result = EvidenceContext(self.market_service, policy_version=market_period_policy_key).apply(result, roles, stamp)
        return result

    def evidence_for(self, role):
        """Per-role public source facts and applicability; no internal market matrix."""
        from .market_evidence import EvidenceContext, make_source_passage
        stamp = self.as_of or datetime.now(timezone.utc).isoformat()
        current = self._market(role['role_id'], 'current', stamp)
        context = EvidenceContext(self.market_service)
        records = context.records(role, stamp, current)
        return dict(policy_version=MARKET_POLICY,
                    records=records,passages=[make_source_passage(r,MARKET_POLICY) for r in records],
                    limitation='Source facts retain their measurement and mapping scope. Context is not a narrow-role quantity.')

    def verify_evidence_passage(self, role, payload):
        from .market_evidence import EvidenceContext
        return EvidenceContext(self.market_service,policy_version=payload['evidence_policy_id']).verify_passage(payload,role)
