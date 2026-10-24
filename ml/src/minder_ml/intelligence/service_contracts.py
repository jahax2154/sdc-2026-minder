"""G0 additive DTO boundary; no new scorer, provider, persistence or training.

Existing recommendation-v1/G1A APIs remain authoritative for legacy preparation.
New lane implementations use these Protocols and JSON-serializable DTOs.
"""
import calendar
import copy
from datetime import date, datetime
from functools import lru_cache
import json
import math
import hashlib
from pathlib import Path
from typing import Dict, List, Protocol

from jsonschema import Draft202012Validator, FormatChecker, validators
from jsonschema.exceptions import ValidationError

CONTRACT_VERSION = 'minder-parallel-v1'
ROOT = Path(__file__).resolve().parents[4]


@lru_cache(maxsize=1)
def _schema():
    schema = json.loads((ROOT / 'contracts/parallel-services.v1.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    return schema


def next_calendar_quarter(issued_at):
    """Next full calendar quarter, not a rolling 90-day horizon."""
    issue = datetime.fromisoformat(issued_at.replace('Z', '+00:00'))
    month = ((issue.month - 1) // 3 + 1) * 3 + 1
    year = issue.year + (month > 12)
    month = 1 if month > 12 else month
    end_month = month + 2
    return {'start': date(year, month, 1).isoformat(),
            'end': date(year, end_month, calendar.monthrange(year, end_month)[1]).isoformat()}


def _json_identity(value):
    """Hashable JSON equality, including distinct booleans and equal 1/1.0."""
    if value is None:
        return ('null',)
    if isinstance(value, bool):
        return ('boolean', value)
    if isinstance(value, (int, float)) and math.isfinite(value):
        return ('number', value)
    if isinstance(value, str):
        return ('string', value)
    if isinstance(value, list):
        return ('array', tuple(_json_identity(v) for v in value))
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return ('object', tuple(sorted((k, _json_identity(v)) for k,v in value.items())))
    raise TypeError('not_finite_json')


def _linear_unique(validator, unique, instance, schema):
    if not unique or not validator.is_type(instance, 'array'):
        return
    try:
        seen = set()
        for value in instance:
            key = _json_identity(value)
            if key in seen:
                yield ValidationError('Array has non-unique elements')
                return
            seen.add(key)
    except (TypeError, ValueError, OverflowError):
        # Preserve stock behavior for non-JSON Python values at internal callers.
        yield from Draft202012Validator.VALIDATORS['uniqueItems'](validator, unique, instance, schema)


_DTOValidator = validators.extend(Draft202012Validator, {'uniqueItems': _linear_unique})


@lru_cache(maxsize=128)
def _validator(kind):
    target = dict(_schema(), **{'$ref': '#/$defs/' + kind})
    target.pop('oneOf', None)
    return _DTOValidator(target, format_checker=FormatChecker())


def validate(kind, payload):
    """Structural and cross-field boundary checks, not evidence approval."""
    schema = _schema()
    if kind not in schema['$defs']:
        raise ValueError('unknown contract kind')
    _validator(kind).validate(payload)
    if kind == 'Evidence':
        if (payload['state'] == 'unknown') != (payload['value'] is None):
            raise ValueError('unknown differs from known zero')
    elif kind in ('Profile', 'Role'):
        evidence = payload['evidence' if kind == 'Profile' else 'requirements']
        if len({e['evidence_id'] for e in evidence}) != len(evidence):
            raise ValueError('duplicate evidence_id')
        for item in evidence:
            validate('Evidence', item)
        if kind == 'Profile':
            keys = [(p['entity_type'], p['entity_id']) for p in payload['preferences']]
            if len(set(keys)) != len(keys):
                raise ValueError('preference is one state per scoped entity, not click penalties')
    elif kind == 'PersonalAssessment':
        scored = payload['score_status'] == 'scored'
        if scored != (payload['score'] is not None):
            raise ValueError('only scored assessments carry numeric scores')
        provisional = (payload['policy_version'] == 'personal-role-fit-v3-provisional'
                       and payload['policy_status'] == 'provisional'
                       and payload['measurement'] == 'personal_role_evidence_fit_v3')
        if scored and provisional:
            coverage = payload.get('assessment_coverage', {})
            components = {c['component_id']: c for c in payload['components']}
            if (not coverage.get('minimum_met') or coverage.get('assessed_count', 0) < 3
                    or coverage.get('fraction', 0) < .3
                    or not coverage.get('required_count')
                    or abs(coverage['fraction'] - coverage['assessed_count'] / coverage['required_count']) > 1e-9
                    or components.get('capability', {}).get('value') is None
                    or any(c['value'] is None and (c['weight'] != 0 or c.get('contribution_points') != 0)
                           for c in payload['components'])):
                raise ValueError('v3 scoring requires anchored minimum; unknown optional inputs have no effect')
            expected = min(100, max(0, sum(c['contribution_points'] for c in components.values())))
            if abs(payload['score'] - expected) > 1e-7:
                raise ValueError('v3 score differs from explicit component contributions')
        elif scored and (payload['policy_status'] != 'accepted' or payload['unknowns']
                       or not payload['components']
                       or any(c['value'] is None or c['weight'] is None
                              for c in payload['components'])):
            raise ValueError('scoring requires accepted policy and complete components')
    elif kind == 'EvidencePassage':
        validate('MarketEvidence', payload['record'])
        if (payload['evidence_id'] != payload['record']['evidence_id']
                or payload['source_record_refs'] != payload['record'].get('source_record_refs', [])
                or payload['passage_sha256'] != hashlib.sha256(payload['canonical_passage'].encode()).hexdigest()):
            raise ValueError('passage identity, source references or hash differ')
    elif kind == 'MarketEvidence':
        period = payload['observation_period']
        if period['start'] and period['end'] and period['start'] > period['end']:
            raise ValueError('reversed evidence period')
        if payload['status'] == 'available':
            if (payload['value'] is None or not math.isfinite(payload['value']) or not payload['source']
                    or not payload['available_at'] or (not payload['published_at']
                        and payload['measurement_type'] != 'occupation_shortage')):
                raise ValueError('available typed evidence requires actual value/source/dates')
            issue = datetime.fromisoformat(payload['as_of'].replace('Z', '+00:00'))
            for key in ('published_at', 'available_at'):
                if payload[key] is None:
                    continue
                stamp = datetime.fromisoformat(payload[key].replace('Z', '+00:00'))
                if stamp.tzinfo is None or stamp > issue:
                    raise ValueError('typed evidence not yet available')
        elif payload['value'] is not None or not payload['missing_reasons']:
            raise ValueError('unavailable typed evidence stays unknown')
        if payload['measurement_type'] == 'sector_context' and payload['ranking_eligibility'] not in ('context_only', 'unsupported'):
            raise ValueError('sector totals cannot become narrow-role ranking quantities')
        if payload['measurement_type'] == 'occupation_shortage' and payload['value'] not in (1, None):
            raise ValueError('shortage positive designation only; unlisted is unknown')
    elif kind == 'MarketResult':
        if payload['observation_period']['start'] > payload['observation_period']['end']:
            raise ValueError('reversed observation period')
        if payload['kind'] == 'forecast':
            if (payload['horizon'] != 'next_full_calendar_quarter'
                    or payload['target_period'] != next_calendar_quarter(payload['issued_at'])):
                raise ValueError('forecast must target next full calendar quarter')
        elif payload['target_period'] is not None or payload['horizon'] != 'observed':
            raise ValueError('current evidence cannot carry a forecast target')
        if payload['status'] == 'unavailable':
            if (payload['value'] is not None or payload['internal_index'] is not None
                    or not payload['missing_reasons']
                    or any(v is not None for v in payload['uncertainty'].values())):
                raise ValueError('unavailable means unknown, never fabricated zero/interval')
        elif (payload['value'] is None or not payload['source_ids']
              or not payload['published_at'] or not payload['available_at']
              or not payload['ingested_at']):
            raise ValueError('available market result requires value, dates and sources')
    elif kind == 'Recommendation':
        for item in payload['internal']['personal_assessments']:
            validate('PersonalAssessment', item)
        for key, expected in [('current_market', 'current'), ('forecast_market', 'forecast')]:
            for item in payload['internal'][key]:
                validate('MarketResult', item)
                if item['kind'] != expected:
                    raise ValueError('current/forecast arrays cannot be mixed')
        public = payload['public']
        candidates = set(public['candidate_ids'])
        if any(o['role_id'] not in candidates for o in public['options']):
            raise ValueError('option outside declared candidates')
        if public['market_period_policy_key'] == 'personal_only_pending_market_policy':
            if payload['internal']['combined_scores']:
                raise ValueError('pending market policy cannot produce blended scores')
        if public['market_period_policy_key'] in ('personal-current-cohort-v1', 'personal-current-evidence-v2', 'personal-current-evidence-v2.1'):
            options = {o['role_id']: o for o in public['options']}
            grouped = []
            for group in public['ranking_groups']:
                for rank, rid in enumerate(group['role_ids'], 1):
                    if rid not in options or options[rid]['rank'] != rank or options[rid]['ranking_group'] != group['group_id']:
                        raise ValueError('rank must match its explicit independent group')
                    grouped.append(rid)
            if len(grouped) != len(set(grouped)) or any(o['rank'] is not None and o['role_id'] not in grouped for o in options.values()):
                raise ValueError('ranked option must belong to exactly one group')
            comparable = [g for g in public['ranking_groups'] if g['basis'] in
                          ('personal_and_comparable_current', 'personal_and_published_offerings')]
            complete = (bool(candidates) and sum(len(g['role_ids']) for g in comparable) == len(candidates)
                        and len(public['ranking_groups']) == len(comparable) == 1)
            if public['overall_ranking_complete'] != complete or (public['status'] == 'available') != complete:
                raise ValueError('personal-only/partial coverage cannot claim full completion')
        if public['market_period_policy_key'] in ('personal-current-evidence-v2', 'personal-current-evidence-v2.1'):
            for row in payload['internal']['evidence_records']:
                validate('MarketEvidence', row)
            for row in payload['internal']['recommendation_traces']:
                validate('RecommendationTrace', row)
    elif kind == 'CompanyRoleResult':
        if payload['status'] == 'found' and (not payload['role_id'] or not payload['official_evidence']):
            raise ValueError('found company role requires official evidence')
        if not payload['searched_scope']:
            raise ValueError('company result must disclose searched scope')
    elif kind == 'PlanProgress':
        if set(payload['task_ids']) != {t['task_id'] for t in payload['tasks']}:
            raise ValueError('plan task index must match tasks')
    elif kind == 'Action':
        direct = payload['origin'] == 'direct_request'
        if direct and not payload['authorizing_request_id']:
            raise ValueError('direct request needs authorizing request ID')
        if not direct and (not payload['proposal_id'] or payload['approval_state'] == 'not_required_direct'):
            raise ValueError('inferred actions require proposal and approval')
        if payload['approval_state'] == 'approved' and (
                not payload['proposal_id'] or payload['approved_proposal_id'] != payload['proposal_id']):
            raise ValueError('approval must identify this exact proposal')
        if payload['execution_status'] == 'applied':
            authorized = ((direct and payload['approval_state'] == 'not_required_direct')
                          or payload['approval_state'] == 'approved')
            if not authorized or not payload['resulting_state_version']:
                raise ValueError('applied action needs authority and resulting version')
    return payload


def public_recommendation(result):
    """C uses this allowlisted DTO; internal market matrices never serialize."""
    validate('Recommendation', result)
    return copy.deepcopy(result['public'])


def legacy_preparation_recommendation(profile, roles, **kwargs):
    """Reuse the actual service; never relabel its output as new role fit."""
    from .inference import recommend_profile
    return recommend_profile(profile, roles, **kwargs)


class PersonalService(Protocol):
    def assess(self, profile: Dict, roles: List[Dict], *, scorer_kind: str,
               policy_version: str, market_period_policy_key: str) -> Dict:
        """Return validated Recommendation; pending policy returns no new score."""
        ...


class MarketService(Protocol):
    def current(self, entity_type: str, entity_id: str, *, as_of: str) -> Dict:
        """Return validated MarketResult(kind=current)."""
        ...

    def forecast(self, entity_type: str, entity_id: str, *, issued_at: str) -> Dict:
        """Return MarketResult(kind=forecast), including explicit unavailable."""
        ...


class EvidenceService(Protocol):
    def evidence_for(self, role: Dict) -> Dict:
        """Typed records/passages with source and mapping scope, no private text."""
        ...

    def verify_evidence_passage(self, role: Dict, payload: Dict) -> Dict:
        """Recompute against actual committed source records; ID alone is insufficient."""
        ...

class ApplicationAdapter(Protocol):
    def career_context(self, profile_id: str, *, expected_profile_version: str) -> Dict:
        """Compose service DTOs; explain saved results without changing scores."""
        ...

    def execute(self, action: Dict, *, expected_state_version: str) -> Dict:
        """C implements persisted, atomic authority/version/idempotency checks."""
        ...
