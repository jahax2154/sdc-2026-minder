"""Deterministic FIT-01..12 measurements; no imputation, model or label creation."""
import math
import hashlib
from .features import build_features, criterion_gaps, time_feasibility
from .schemas import FEATURE_NAMES, number, nonempty
from .policy import ROOT, fingerprint, load_policy

VERSION = 'policy-feature-pipeline-g1a-v1.1'


def _evidence_ids(value, *, required=False):
    """Evidence references are distinct nonempty IDs, never a truthy string."""
    if value is None:
        value = []
    if not isinstance(value, list) or (required and not value):
        raise ValueError('evidence_ids must be a list of nonempty evidence IDs')
    for identifier in value:
        nonempty(identifier, 'evidence_id')
    if len(value) != len(set(value)):
        raise ValueError('duplicate evidence_id')
    return value


def _unique(rows, key):
    ids = [nonempty(r[key], key) for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate ' + key)


def validate_milestone(m):
    for key in ('milestone_id', 'version', 'target_artifact'):
        nonempty(m.get(key), key)
    if m.get('scope') != 'initial_preparation':
        raise ValueError('full occupation is not an initial milestone')
    criteria = m.get('criteria', [])
    if not criteria:
        raise ValueError('invalid_requirement_catalogue: no required criteria')
    _unique(criteria, 'criterion_id')
    for row in criteria:
        if row.get('weight', 1) != 1:
            raise ValueError('non-default weights require a separately implemented named policy')
        if set(row.get('anchors', {})) != {'0', '0.5', '1'}:
            raise ValueError('criterion requires explicit 0/0.5/1 anchors')
        for value in row['anchors'].values():
            nonempty(value, 'content anchor')
        nonempty(row.get('anchor_version'), 'anchor_version')
        _evidence_ids(row.get('evidence_ids'), required=True)
    # Absent lists mean unknown, explicitly empty lists mean no requirements.
    for key, identifier in (('interest_tags', 'tag_id'), ('work_style_tags', 'tag_id'),
                            ('resource_groups', 'group_id'), ('tasks', 'task_id'),
                            ('hard_requirements', 'requirement_id')):
        if key not in m or m[key] is None:
            raise ValueError('missing milestone definition: ' + key)
        _unique(m[key], identifier)
        for row in m[key]:
            if row.get('weight', 1) != 1:
                raise ValueError('unsupported weight override')
            _evidence_ids(row.get('evidence_ids'), required=True)
    for group in m['resource_groups']:
        if not group.get('alternatives'):
            raise ValueError('empty resource alternatives')
        _unique(group['alternatives'], 'alternative_id')
        for alt in group['alternatives']:
            if 'cost' in alt:
                number(alt['cost'], 'resource cost')
                nonempty(alt.get('currency'), 'resource currency')
                nonempty(alt.get('period'), 'resource period')
    tasks = {t['task_id']: t for t in m['tasks']}
    visited, active = set(), set()
    def visit(key):
        if key in active or key not in tasks:
            raise ValueError('cyclic or missing prerequisite')
        if key in visited:
            return
        active.add(key)
        t = tasks[key]
        nonempty(t.get('version'), 'task version')
        if t.get('effort') is not None:
            e = t['effort']
            if e.get('unit') != 'hours' or not e.get('basis') or not e.get('evidence_ids'):
                raise ValueError('effort requires hours, source/estimate basis and evidence')
            _evidence_ids(e['evidence_ids'], required=True)
            low = number(e['low'], 'effort low')
            high = number(e['high'], 'effort high')
            if low > high:
                raise ValueError('inverted effort range')
        for parent in t.get('prerequisites', []):
            visit(parent)
        active.remove(key)
        visited.add(key)
    for key in tasks:
        visit(key)
    return m


def _answers(rows, key):
    _unique(rows, key)
    for row in rows:
        _evidence_ids(row.get('evidence_ids'))
    return {r[key]: r for r in rows}


def _explicit(row, values):
    if not row or not row.get('evidence_ids'):
        return None
    value = row.get('value')
    if value is None:
        return None
    if value not in values:
        raise ValueError('invalid explicit utility: ' + str(value))
    return values[value]


def _mean(values):
    return None if not values or any(v is None for v in values) else math.fsum(values) / len(values)


def derive_features(profile, role, answers=None):
    """Shared builder for a policy-accepted bounded milestone, with versioned sidecar.

    `answers` is an explicit structured measurement supplement, not free-text mining.
    Assessments bind criterion, milestone and anchor versions and evidence basis.
    """
    _, active = load_policy()
    nonempty(profile.get('profile_id'), 'profile_id')
    nonempty(profile.get('version'), 'profile version')
    answers = answers or {}
    horizon = profile.get('planning_horizon', {}).get('weeks', 12)
    number(horizon, 'horizon')
    if horizon <= 0:
        raise ValueError('horizon must be positive')
    h = profile.get('hours_per_week')
    if h is not None:
        number(h, 'hours_per_week')
    dependencies = {}
    source_error = False
    refs = list(role.get('sources', []))
    if role.get('milestone') and role['milestone'].get('acceptance'):
        proof = role['milestone']['acceptance']
        if proof.get('source_path'):
            refs.append({'path': proof['source_path'], 'sha256': proof.get('sha256')})
    for ref in refs:
        path = (ROOT / ref['path']).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('source path outside repository')
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        dependencies[ref['path']] = actual_hash
        source_error = source_error or actual_hash != ref.get('sha256')
    registry_path = ROOT / 'ml/configs/intelligence/measurement_sources.v1.json'
    dependencies['measurement_source_registry'] = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    result = {'pipeline_version': VERSION, 'role_id': role['role_id'], 'role_version': role.get('version'),
              'profile_version': profile['version'], 'policy': active,
              'input_fingerprint': fingerprint({'profile': profile, 'role': role,
                                                'answers': answers, 'policy': active,
                                                'pipeline': VERSION, 'source_dependencies': dependencies}),
              'catalogue_status': 'invalid_catalogue', 'feature_components': dict.fromkeys(FEATURE_NAMES),
              'assessed_requirement_fraction': None, 'eligible': False, 'criterion_gaps': [],
              'questions': [], 'exceptions': [], 'traces': {}, 'evidence_ids': [],
              'constraint_status': 'needs_check', 'snapshot': None}
    if source_error:
        result['exceptions'] = ['source_dependency_changed_or_missing']
        result['questions'] = ['Restore the pinned source or revalidate and version its source projection.']
        return result
    m = role.get('milestone')
    if m is None:
        result['exceptions'] = ['milestone_definition_missing']
        result['missing_evidence'] = {
            'criteria': [{'criterion_id': c['criterion_id'],
                          'missing': ['content_anchors_0_0.5_1', 'anchor_version', 'accepted_task_template']}
                         for c in role.get('pending_criteria', [])],
            'milestone': ['target_artifact', 'task_prerequisite_graph', 'sourced_effort_hours',
                          'explicit_interest_tags', 'resource_alternative_groups', 'sourced_work_style_tags',
                          'explicit_hard_requirements_or_confirmed_empty_list'],
            'profile_measurements': ['version_bound_criterion_answers', 'interest_tag_answers',
                                     'resource_access_and_compatible_budget', 'work_style_utilities']}
        result['known_inputs'] = {'hours_per_week': h, 'horizon_weeks': horizon}
        result['questions'] = ['Supply a bounded milestone with anchored criteria, sourced task effort, interest tags, resource groups and work-style tags.']
        return result
    try:
        validate_milestone(m)
        if m.get('role_id') != role['role_id']:
            raise ValueError('milestone role scope mismatch')
        if m.get('status') != 'policy_accepted' or not m.get('acceptance'):
            raise ValueError('milestone lacks policy acceptance provenance')
        from .policy_sources import verify_milestone_acceptance
        verify_milestone_acceptance(m)
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as exc:
        result['exceptions'] = ['invalid_catalogue: ' + str(exc)]
        result['questions'] = ['Correct the milestone definition or pinned source: ' + str(exc)]
        return result
    result['catalogue_status'] = 'policy_accepted'
    result['milestone_version'] = m['version']
    result['acceptance'] = m['acceptance']
    result['provenance_class'] = m['provenance_class']
    evidence = {'policy:' + active['policy_sha256'],
                'template:' + m['acceptance'].get('record_sha256', 'synthetic-test-only')}
    for collection in ('criteria', 'tasks', 'interest_tags', 'work_style_tags', 'resource_groups', 'hard_requirements'):
        for definition in m[collection]:
            evidence.update(definition.get('evidence_ids', []))
            if definition.get('effort'):
                evidence.update(definition['effort'].get('evidence_ids', []))
    if answers and (answers.get('profile_version') != profile['version'] or answers.get('milestone_version') != m['version']):
        result['exceptions'].append('measurement_supplement_version_mismatch')
        answers = {}
    assessments = _answers(answers.get('criterion_assessments', []), 'criterion_id')
    requirements = []
    trace = []
    for c in m['criteria']:
        row = assessments.get(c['criterion_id'])
        value = None
        if row and row.get('milestone_version') == m['version'] and row.get('anchor_version') == c['anchor_version']:
            value = row.get('value')
            if value is not None:
                if (isinstance(value, bool) or value not in (0, .5, 1)
                        or row.get('basis') not in ('anchored_self_report', 'assessed', 'demonstrated')
                        or not row.get('evidence_ids')):
                    raise ValueError('criterion assessment requires explicit anchor, basis and evidence')
                evidence.update(row['evidence_ids'])
        requirements.append({'criterion_id': c['criterion_id'], 'requirement_weight': 1,
                             'demonstrated_fraction': value})
        trace.append({'criterion_id': c['criterion_id'], 'value': value,
                      'basis': row.get('basis') if row and value is not None else None,
                      'anchor': c['anchors'].get({0: '0', .5: '0.5', 1: '1'}.get(value)) if value is not None else None,
                      'rule_id': 'FIT-04', 'evidence_ids': row.get('evidence_ids', []) if row else [],
                      'definition_evidence_ids': c['evidence_ids']})
    def utility(key, mapping):
        by_id = _answers(answers.get(key, []), 'tag_id')
        values, records = [], []
        for tag in m[key]:
            row = by_id.get(tag['tag_id'])
            value = _explicit(row, mapping)
            if row and value is not None:
                evidence.update(row['evidence_ids'])
            values.append(value)
            records.append({'tag_id': tag['tag_id'], 'value': value,
                            'evidence_ids': row.get('evidence_ids', []) if row else [],
                            'definition_evidence_ids': tag['evidence_ids']})
        return _mean(values), records
    interest, interest_trace = utility('interest_tags', {'dislike': 0, 'avoid': 0, 'neutral': .5, 'open': .5, 'interested': 1})
    work, work_trace = utility('work_style_tags', {'incompatible': 0, 'neutral': .5, 'acceptable': .5, 'compatible': 1, 'no_preference': .5})
    resource_answers = _answers(answers.get('resources', []), 'alternative_id')
    groups = []
    for group in m['resource_groups']:
        alternatives = []
        for alt in group['alternatives']:
            row = resource_answers.get(alt['alternative_id'])
            value = _explicit(row, {'accessible': 1, 'unavailable': 0})
            # Price is only one requirement; an affordable price never proves access.
            if 'cost' in alt and alt['cost'] > 0 and value != 0:
                budget = answers.get('budget', {})
                if (budget.get('currency') != alt['currency'] or budget.get('period') != alt['period']
                        or budget.get('amount') is None or not budget.get('evidence_ids')):
                    value = None
                else:
                    number(budget['amount'], 'budget')
                    _evidence_ids(budget['evidence_ids'], required=True)
                    evidence.update(budget['evidence_ids'])
                    if budget['amount'] < alt['cost']:
                        value = 0
            if row and value is not None:
                evidence.update(row['evidence_ids'])
            alternatives.append({'alternative_id': alt['alternative_id'], 'value': value})
        vals = [a['value'] for a in alternatives]
        v = 1 if 1 in vals else 0 if all(v == 0 for v in vals) else None
        groups.append({'group_id': group['group_id'], 'value': v, 'alternatives': alternatives})
    resource = _mean([g['value'] for g in groups]) if groups else 1.0
    completed = _answers(answers.get('completed_tasks', []), 'task_id')
    low = high = 0.0
    task_trace = []
    for task in m['tasks']:  # Unique task catalogue includes the prerequisite closure exactly once.
        done = completed.get(task['task_id'], {})
        is_done = (done.get('task_version') == task['version'] and bool(done.get('evidence_ids'))
                   and done.get('completed') is True)
        effort = task.get('effort')
        if is_done:
            evidence.update(done['evidence_ids'])
        elif effort is None:
            low = high = None
        elif high is not None:
            low += effort['low']
            high += effort['high']
        task_trace.append({'task_id': task['task_id'], 'completed': is_done,
                           'effort': effort, 'rule_id': 'FIT-06'})
    constraints = _answers(answers.get('constraint_checks', []), 'requirement_id')
    declarations = _answers(answers.get('hard_constraints', []), 'constraint_id')
    checks = []
    for req in m['hard_requirements']:
        row = constraints.get(req['requirement_id'])
        value = _explicit(row, {'compatible': 1, 'conflict': 0})
        # A check must cite an actual user-declared hard constraint; no title inference.
        declaration = declarations.get(row.get('constraint_id')) if row else None
        if not declaration or declaration.get('declared_by_user') is not True or not declaration.get('statement') or not declaration.get('evidence_ids'):
            value = None
        if row and value is not None:
            evidence.update(row['evidence_ids'])
        if declaration and value is not None:
            evidence.update(declaration['evidence_ids'])
        checks.append({'requirement_id': req['requirement_id'],
                       'constraint_id': row.get('constraint_id') if row else None,
                       'value': value})
    # An explicit user constraint that has not been matched is unresolved,
    # even when the milestone has a confirmed empty hard-requirement list.
    checked_constraints = {c['constraint_id'] for c in checks if c['value'] is not None}
    for identifier, declaration in declarations.items():
        if declaration.get('declared_by_user') is True and identifier not in checked_constraints:
            checks.append({'requirement_id': None, 'constraint_id': identifier,
                           'value': None, 'reason': 'user_constraint_not_resolved'})
    state = 'excluded' if any(c['value'] == 0 for c in checks) else 'needs_check' if any(c['value'] is None for c in checks) else 'clear'
    snapshot = build_features([(r['requirement_weight'], r['demonstrated_fraction']) for r in requirements],
                              interest, resource, work, h, high, horizon,
                              effort_low_hours=low, effort_high_hours=high)
    result.update(feature_components=snapshot.components(),
                  assessed_requirement_fraction=snapshot.assessed_requirement_fraction,
                  eligible=snapshot.eligible and state == 'clear', constraint_status=state,
                  criterion_gaps=criterion_gaps(requirements), snapshot=snapshot,
                  evidence_ids=sorted(evidence),
                  traces={'C': {'rule_id': 'FIT-04', 'criteria': trace},
                          'I': {'rule_id': 'FIT-05', 'tags': interest_trace},
                          'T': {'rule_id': 'FIT-06', 'tasks': task_trace, 'effort_low': low, 'effort_high': high,
                                'hours_per_week': h, 'horizon_weeks': horizon, 'T_low': time_feasibility(h, high, horizon), 'T_high': time_feasibility(h, low, horizon)},
                          'R': {'rule_id': 'FIT-07', 'groups': groups},
                          'W': {'rule_id': 'FIT-08', 'tags': work_trace},
                          'constraints': {'rule_id': 'FIT-09', 'checks': checks}})
    if snapshot.assessed_requirement_fraction < 1 - 1e-9:
        result['exceptions'].append('incomplete_skill_evidence')
    for name, value in snapshot.components().items():
        if value is None:
            result['exceptions'].append('missing_' + name)
            result['questions'].append('Provide explicit evidence for ' + name + ' in milestone ' + m['milestone_id'] + '.')
    for gap in result['criterion_gaps']:
        if gap['demonstrated_fraction'] is None:
            result['questions'].append('Answer the 0/0.5/1 anchors for criterion ' + gap['criterion_id'] + '.')
    if state != 'clear':
        result['exceptions'].append('hard_constraint_' + state)
        result['questions'].append('Resolve the explicit hard-requirement checks before ranking; excluded options need an alternative milestone.')
    return result
