"""Source-backed read presentation. Never turn occupation ratings into user ability."""
import copy
from datetime import datetime, timezone
from minder_ml.intelligence.role_fit import _valid_skill
from minder_ml.intelligence.service_contracts import validate
from .store import AppError

VERSION = 'role-display-v1'
MEASURES = {
    'onet:IM': ('Occupational importance', 'How important this skill is in the occupation.'),
    'onet:LV': ('Occupational activity level', 'The activity level reported for the occupation; not your skill level.'),
}


def resolve_role(app, owner, body):
    if 'role_id' in body:
        identifier = body['role_id']
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 200:
            raise AppError('invalid_role_id', 422)
        origin = 'request'
    else:
        try:
            direction = app.store.get(owner, 'direction', owner)
        except AppError as error:
            if error.status != 404:
                raise
            raise AppError('career_selection_required', 422) from None
        identifier, origin = direction['role_id'], 'saved_direction'
    role = next((r for r in app.services.roles if r['role_id'] == identifier), None)
    if role is None:
        raise AppError('role_not_found', 404)
    return role, dict(role_id=identifier, source=origin)


def presentation(app, owner, role):
    ref = getattr(app.services.personal, 'ref', {})
    rubrics = ref.get('skill_rubrics', {})
    try:
        profile = app.store.get(owner, 'profile', owner)
    except AppError as error:
        if error.status != 404:
            raise
        profile = None
    grouped = {}
    for row in role.get('requirements', []):
        identifier = row['subject_id']
        if identifier not in grouped:
            rubric = rubrics.get(identifier, {})
            observations = [e for e in (profile or {}).get('evidence', []) if e['subject_id'] == identifier]
            # Presence is not competence, and text confidence is not a numerical assessment.
            anchored = [e for e in observations if _valid_skill(e, ref)] if rubrics else []
            conflicting = len({e['value'] for e in anchored}) > 1
            kinds = sorted({e.get('assessment', {}).get('kind', 'unclassified') for e in observations})
            personal = dict(status='needs_clarification' if conflicting else
                'anchored_evidence_recorded' if anchored else 'recorded_unassessed' if observations else 'not_assessed',
                recorded_count=len(observations), anchored_count=len(anchored), assessment_kinds=kinds,
                evidence_ids=[e['evidence_id'] for e in observations],
                explanation='Your supporting records need clarification.' if conflicting else
                'Anchored evidence recorded; this alone does not certify competence.' if anchored else
                'Your notes are saved; a numerical skill assessment has not been established.' if observations else
                'You have not supplied an assessment for this skill.')
            grouped[identifier] = dict(subject_id=identifier, label=rubric.get('label'),
                label_status='available' if rubric.get('label') else 'unavailable',
                label_source=copy.deepcopy(ref.get('sources', {}).get('anchors')) if rubric.get('label') else None,
                measurements=[], personal_evidence=personal)
        label, explanation = MEASURES.get(row['unit'], ('Source measurement', 'Read the source for this measurement.'))
        grouped[identifier]['measurements'].append(dict(evidence_id=row['evidence_id'], unit=row['unit'],
            label=label, explanation=explanation, value=copy.deepcopy(row.get('value')),
            availability='available' if row['state'] == 'known' and row.get('value') is not None else 'unavailable',
            source=copy.deepcopy(row['provenance'])))
    return dict(version=VERSION, role_id=role['role_id'], role_label=role['label'],
        skills=list(grouped.values()), source_record_count=len(role.get('requirements', [])),
        skill_count=len(grouped),
        explanation='These US occupational reference ratings describe the work. They are not Malaysian hiring requirements or your competence.',
        measurement_rule='Importance and activity level are different measures. All original source records are retained; none are averaged or silently deduplicated.')


def forecast_view(app, role):
    """An independent forecast read must not suppress current observations."""
    if app.services.market is None:
        return dict(forecast=None, forecast_error='forecast_service_unavailable')
    try:
        result = app.services.market.forecast('role', role['role_id'],
            issued_at=datetime.now(timezone.utc).isoformat())
        validate('MarketResult', result)
        if result['entity_id'] != role['role_id'] or result['entity_type'] != 'role' or result['kind'] != 'forecast':
            raise ValueError('forecast_scope_mismatch')
        return dict(forecast=result, forecast_error=None)
    except Exception:
        # Source data and provider exceptions can contain sensitive details. Return
        # only a bounded status; no invented forecast, exception text or retry.
        return dict(forecast=None, forecast_error='forecast_read_failed')
