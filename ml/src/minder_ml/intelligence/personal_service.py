"""Initial role assessment while N01 is pending; never execute proposal weights.

Requirements are occupational references, not competence rubrics. Matching a
subject identifier preserves evidence but cannot establish a met/gap judgment.
No legacy preparation model or preparation feature is used for this target.
"""
import copy
import json

from .policy import ROOT, fingerprint
from .service_contracts import CONTRACT_VERSION, validate

POLICY_VERSION = 'personal-role-fit-v2-proposal'
MARKET_POLICY = 'personal_only_pending_market_policy'


def update_preference(profile, *, entity_type, entity_id, state,
                      authorizing_request_id, expected_profile_version):
    """Return a new Profile for C to persist atomically; no database mutation.

    Reset (`unknown`) removes only this scoped preference. Repeated same-state
    feedback is a no-op, including the version; request retries add no penalty.
    C still owns request deduplication and transactional version checks.
    """
    validate('Profile', profile)
    if expected_profile_version != profile['version']:
        raise ValueError('stale_profile_version')
    preference = dict(entity_type=entity_type, entity_id=entity_id, state=state,
                      authorizing_request_id=authorizing_request_id)
    validate('Preference', preference)
    key = (entity_type, entity_id)
    old = next((p for p in profile['preferences']
                if (p['entity_type'], p['entity_id']) == key), None)
    if (old is None and state == 'unknown') or (old is not None and old['state'] == state):
        return copy.deepcopy(profile)
    updated = copy.deepcopy(profile)
    updated['preferences'] = [p for p in updated['preferences']
                              if (p['entity_type'], p['entity_id']) != key]
    if state != 'unknown':
        updated['preferences'].append(preference)
    updated['preferences'].sort(key=lambda p: (p['entity_type'], p['entity_id']))
    updated['version'] = 'profile-feedback-v1:' + fingerprint(updated)
    return validate('Profile', updated)


def filter_roles(roles, view_filter=None):
    """Explicit view restriction, independent of preferences and saved catalogue.

    None clears the restriction. Empty allowed-ID lists intentionally match no
    records. Industry filters use accepted links only; disclose unknown mappings.
    This returns an inspectable filter report for C's visible/reversible view.
    """
    if view_filter is None:
        return dict(roles=copy.deepcopy(roles), applied_filter=None,
                    excluded_role_ids=[], unresolved_industry_role_ids=[], unmatched_role_ids=[])
    validate('SearchFilter', view_filter)
    selected, excluded, unresolved = [], [], []
    for role in roles:
        validate('Role', role)
        accepted = {m['target_id'] for m in role['industry_mappings']
                    if m['status'] in ('source_accepted', 'policy_accepted')}
        allowed_roles, allowed_industries = view_filter['role_ids'], view_filter['industry_ids']
        match = allowed_roles is None or role['role_id'] in allowed_roles
        if allowed_industries is not None:
            if not accepted:
                unresolved.append(role['role_id'])
            match = match and bool(accepted & set(allowed_industries))
        if view_filter['query'] is not None:
            match = match and view_filter['query'].casefold() in role['label'].casefold()
        (selected if match else excluded).append(role if match else role['role_id'])
    return dict(roles=copy.deepcopy(selected), applied_filter=copy.deepcopy(view_filter),
                excluded_role_ids=excluded, unresolved_industry_role_ids=unresolved,
                unmatched_role_ids=sorted(set(view_filter['role_ids'] or []) - {r['role_id'] for r in roles}))


def industry_context(profile, role):
    """Keep history, intent and valid many-to-many links separate; no arithmetic."""
    mappings = {m['target_id'] for m in role['industry_mappings']
                if m['status'] in ('source_accepted', 'policy_accepted')}
    fields = [f for f in profile['current_fields'] if f['field_type'] == 'industry'
              and f['state'] in ('known', 'want_to_leave')]
    preferences = {p['entity_id']: p for p in profile['preferences'] if p['entity_type'] == 'industry'}
    ids = mappings | {f['field_id'] for f in fields} | set(preferences)
    result = []
    for iid in sorted(ids):
        background = [copy.deepcopy(f) for f in fields if f['field_id'] == iid]
        result.append(dict(
            industry_id=iid, background=None, preference_utility=None, assessment=None,
            rule_id='D03-context-N01-pending',
            evidence_ids=sorted({e for f in background for e in f['evidence_ids']}),
            missing_reasons=['N01_pending', 'background_is_not_anchored_capability']
            + ([] if iid in mappings else ['role_industry_mapping_unavailable']),
            background_fields=background, preference=copy.deepcopy(preferences.get(iid)),
            role_mapping_status='supported' if iid in mappings else 'unknown'))
    return result


class PersonalMatchingService:
    """Concrete implementation of PersonalService's JSON boundary for C.

    Candidate order is supplied catalogue order, never an asserted ranking.
    The pending guard reads the actual inactive config on every call. Approval
    requires a separately implemented migration; toggling a flag cannot activate.
    Market service is optional and must implement the committed B protocol.
    """

    def __init__(self, market_service=None, *, as_of=None):
        if market_service is not None and as_of is None:
            raise ValueError('market calls require explicit as_of/issue timestamp')
        self.market_service, self.as_of = market_service, as_of

    def assess(self, profile, roles, *, scorer_kind='baseline', policy_version=POLICY_VERSION,
               market_period_policy_key=MARKET_POLICY):
        config = json.loads((ROOT / 'ml/configs/intelligence/role-fit.v2.proposed.json').read_text())
        if (policy_version != POLICY_VERSION or config['policy_id'] != policy_version
                or config['status'] != 'pending' or config['active'] is not False):
            raise ValueError('unsupported numerical policy; explicit approved implementation required')
        if scorer_kind not in ('baseline', 'ridge', 'xgboost'):
            raise ValueError('unknown scorer_kind')
        if market_period_policy_key != MARKET_POLICY:
            raise ValueError('no approved current/forecast combination rule')
        validate('Profile', profile)
        if len({r['role_id'] for r in roles}) != len(roles):
            raise ValueError('duplicate role identity')
        result = dict(public=dict(
            contract_version=CONTRACT_VERSION, profile_id=profile['profile_id'],
            profile_version=profile['version'], policy_version=policy_version,
            model_version=None, candidate_ids=[], market_period_policy_key=MARKET_POLICY,
            status='policy_pending', options=[], limitations=[
                'Numerical personal role-fit policy is pending; options are unranked.',
                'Occupational references do not establish qualification to apply today.',
                'US occupational references are not Malaysian employment measurements.']),
            internal=dict(personal_assessments=[], current_market=[], forecast_market=[],
                          combined_score_policy_version=None, combined_scores=[]))
        if self.market_service is None:
            result['public']['limitations'].append('Market service is not connected; no market observation or forecast supplied.')
        evidence_by_subject = {}
        for evidence in profile['evidence']:
            evidence_by_subject.setdefault(evidence['subject_id'], []).append(evidence)
        role_prefs = {p['entity_id']: p for p in profile['preferences'] if p['entity_type'] == 'role'}
        for role in roles:
            validate('Role', role)
            if role['eligibility'] != 'supported':
                continue
            rid = role['role_id']
            gaps = []
            for subject in sorted({r['subject_id'] for r in role['requirements']}):
                observations = evidence_by_subject.get(subject, [])
                gaps.append(dict(criterion_id=subject, state='unknown',
                                 evidence_ids=[e['evidence_id'] for e in observations],
                                 reason=('Evidence retained; no accepted occupation-to-person assessment rubric.'
                                         if observations else 'No profile evidence for this source skill; competence is unknown.')))
            unknowns = sorted(set(['N01_pending'] + role['missing_reasons']
                                  + (['hard_constraints_not_evaluated'] if any(c['hard'] for c in profile['constraints']) else [])))
            assessment = dict(
                profile_id=profile['profile_id'], profile_version=profile['version'],
                role_id=rid, role_version=role['version'], policy_version=policy_version,
                policy_status='pending', model_version=None, scorer_kind=scorer_kind,
                score_status='policy_pending', score=None, measurement='personal_role_fit',
                components=[dict(component_id=c, value=None, weight=None, unit='fraction_0_1',
                                 rule_id='N01-pending', evidence_ids=[], missing_reasons=['N01_pending'])
                            for c in ('capability', 'preference', 'work_style')],
                industry_contributions=industry_context(profile, role), gaps=gaps,
                prerequisites=[], evidence_ids=sorted({e['evidence_id'] for e in profile['evidence']}),
                unknowns=unknowns,
                targeted_questions=['What project, assessment or work evidence can you provide for the listed occupational skills?'],
                trace_rule_ids=['D01-unknown-is-not-zero', 'D03-no-industry-exclusion',
                                'initial-fit-without-milestones-v1', 'N01-pending'],
                role_preference=copy.deepcopy(role_prefs.get(rid)),
                profile_fields=copy.deepcopy(profile['current_fields']),
                unresolved_constraints=copy.deepcopy(profile['constraints']))
            result['internal']['personal_assessments'].append(assessment)
            explanation = f"{role['label']}: source skill requirements are available; personal fit awaits the scoring policy and a compatible evidence rubric."
            if role_prefs.get(rid, {}).get('state') == 'not_interested':
                explanation += ' Marked Not interested; retained for exploration.'
            result['public']['candidate_ids'].append(rid)
            result['public']['options'].append(dict(
                role_id=rid, rank=None, personal_score=None, score_status='policy_pending',
                explanation=explanation,
                source_ids=sorted({role['source']['source_id']}
                                  | {r['provenance']['source_id'] for r in role['requirements']}),
                unknowns=unknowns))
            if self.market_service is not None:
                for key, method, kwargs in (
                        ('current_market', self.market_service.current, {'as_of': self.as_of}),
                        ('forecast_market', self.market_service.forecast, {'issued_at': self.as_of})):
                    market = method('role', rid, **kwargs)
                    validate('MarketResult', market)
                    if market['entity_type'] != 'role' or market['entity_id'] != rid:
                        raise ValueError('market response entity mismatch')
                    result['internal'][key].append(copy.deepcopy(market))
        if not result['public']['candidate_ids']:
            result['public']['status'] = 'unavailable'
            result['public']['limitations'].append('No supported role references in the supplied view.')
        validate('Recommendation', result)
        return result
