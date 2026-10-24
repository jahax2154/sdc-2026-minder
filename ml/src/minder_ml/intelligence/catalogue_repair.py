"""G1A-R catalogue adapter. Pending templates never enter live inference.

No new scorer. Actual approvals and defensible estimates must be supplied before
activation; approval of a template never creates a user assessment or gold label.
"""
import copy
import hashlib
import json
from pathlib import Path
from .policy import ROOT, fingerprint
from .policy_sources import native_catalogue
from .policy_features import validate_milestone
from .schemas import number, nonempty

BASE = 'ml/data/review/g1a-r-v1'
BATCH = BASE + '/milestone_batch.proposed.json'
FACTS = BASE + '/source_facts.json'


def _path(relative, root=None):
    root = ROOT if root is None else root
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('catalogue input must stay within repository')
    return path


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_source_facts():
    path = _path(FACTS)
    facts = json.loads(path.read_text())
    for capture in facts['captures']:
        if hashlib.sha256(capture['evidence_text'].encode()).hexdigest() != capture['captured_evidence_sha256']:
            raise ValueError('captured source evidence checksum mismatch')
    return facts


def repaired_catalogue():
    """Source-only repair: taxonomy scope and declared equal weight projections.

    Does not turn proposed anchors, resource assumptions or unknown hours into
    accepted milestones. The original pending records remain untouched.
    """
    facts = read_source_facts()
    relation = next(c for c in facts['captures'] if c['source_id'] == 'onet-version-relationship')
    roles = native_catalogue()
    for role in roles:
        if role['identifier']['database_version'] != relation['facts']['database_version']:
            raise ValueError('version relationship not applicable to this database')
        role['identifier']['taxonomy_edition'] = relation['facts']['taxonomy_edition']
        role['taxonomy_evidence'] = {
            'status': 'policy_accepted', 'provenance_class': 'source-derived',
            'rule_id': 'AUTO-01', 'source_id': relation['source_id'],
            'capture_sha256': relation['captured_evidence_sha256'],
            'scope': 'Documented taxonomy/database relationship only; no ESCO mapping adoption.'}
        role['sources'].append({'source_id': 'g1ar-source-captures', 'path': FACTS,
                                'sha256': _sha(_path(FACTS)), 'scope': role['taxonomy_evidence']['scope']})
        role['criterion_policy_defaults'] = [
            {'criterion_id': c['criterion_id'], 'weight': 1.0, 'rule_id': 'FIT-04',
             'status': 'policy_accepted', 'provenance_class': 'policy-derived',
             'scope': 'Default weight only; criterion/milestone inclusion and anchors still pending.'}
            for c in role['pending_criteria']]
        role['upstream_version'] = role['version']
        role['version'] = 'g1ar-reference-v1:' + fingerprint(role)
    return roles


def load_batch(relative=BATCH):
    """Validate a pending batch without activating it or filling absent effort."""
    path = _path(relative)
    batch = json.loads(path.read_text())
    if batch.get('schema_version') != 'g1ar-milestone-batch-v1' or batch.get('status') != 'pending' or batch.get('active') is not False:
        raise ValueError('expected explicitly inactive pending proposal')
    for path_key, hash_key in [('source_facts_path', 'source_facts_sha256'),
                                ('original_role_drafts_path', 'original_role_drafts_sha256')]:
        if _sha(_path(batch[path_key])) != batch[hash_key]:
            raise ValueError('batch source dependency changed: ' + path_key)
    read_source_facts()
    drafts = json.loads(_path(batch['original_role_drafts_path']).read_text())['roles']
    by_role = {r['role_id']: r for r in drafts}
    templates = batch['milestone_templates']
    ids = [m['role_id'] for m in templates]
    if len(ids) != len(set(ids)) or set(ids) != set(by_role):
        raise ValueError('batch must cover exactly the original three roles')
    for milestone in templates:
        validate_milestone(milestone)
        if milestone.get('provenance_class') != 'llm-proposed' or milestone.get('proposal_status') != 'pending' or 'acceptance' in milestone:
            raise ValueError('proposal cannot self-approve')
        expected = {c['criterion_id'] for c in by_role[milestone['role_id']]['criteria']}
        if {c['criterion_id'] for c in milestone['criteria']} != expected:
            raise ValueError('proposal drops or adds an essential draft criterion')
        task_criteria = {c for task in milestone['tasks'] for c in task.get('criterion_ids', [])}
        if task_criteria != expected:
            raise ValueError('tasks must cover both draft criteria')
    instances = batch.get('assessment_instances', [])
    expected_criteria = {c['criterion_id'] for m in templates for c in m['criteria']}
    if {r['criterion_id'] for r in instances} != expected_criteria or len(instances) != len(expected_criteria):
        raise ValueError('provide one concrete assessment instance for every criterion')
    for instance in instances:
        nonempty(instance.get('instance_id'), 'assessment instance ID')
        if instance.get('data_class') != 'synthetic':
            raise ValueError('assessment instances must be explicitly synthetic')
        nonempty(instance.get('prompt'), 'assessment prompt')
        nonempty(instance.get('expected_evidence'), 'expected evidence')
    if len({r['instance_id'] for r in instances}) != len(instances):
        raise ValueError('duplicate assessment instance ID')
    return batch


def activation_plan(relative=BATCH, *, decision_path):
    """Prepare an immutable accepted-source release only after a complete decision.

    This function performs no writes. A decision is a caller-supplied real review
    record; local consistency checks are not proof of a human identity.
    """
    batch = load_batch(relative)
    decision = json.loads(_path(decision_path).read_text())
    digest = _sha(_path(relative))
    if decision.get('schema_version') != 'g1ar-batch-decision-v1' or decision.get('batch_id') != batch['batch_id'] or decision.get('batch_sha256') != digest:
        raise ValueError('decision does not bind this exact batch')
    if decision.get('status') != 'approved':
        raise ValueError('batch decision is not approved; proposals remain inactive')
    for key in ('decision_id', 'reviewer_id', 'decided_at', 'rationale', 'accepted_effort_method_id'):
        nonempty(decision.get(key), key)
    # Require actual scenario/table/brief artifacts, not only abstract rubrics.
    instances = batch['assessment_instances']
    selected = decision.get('assessment_instance_ids', [])
    if len(selected) != len(instances) or set(selected) != {r['instance_id'] for r in instances}:
        raise ValueError('decision must select the exact proposed assessment instances')
    expected_criteria = {c['criterion_id'] for m in batch['milestone_templates'] for c in m['criteria']}
    if {r['criterion_id'] for r in instances} != expected_criteria or len(instances) != len(expected_criteria):
        raise ValueError('provide one concrete assessment instance for every criterion')
    for instance in instances:
        if instance.get('data_class') != 'synthetic':
            raise ValueError('assessment instances must be explicitly synthetic')
        nonempty(instance.get('prompt'), 'assessment prompt')
        nonempty(instance.get('expected_evidence'), 'expected evidence')
    estimates = decision.get('task_effort_estimates', [])
    by_task = {row['task_id']: row for row in estimates}
    task_ids = {t['task_id'] for m in batch['milestone_templates'] for t in m['tasks']}
    if len(by_task) != len(estimates) or set(by_task) != task_ids:
        raise ValueError('one estimate required for every unique task')
    for row in estimates:
        low, high = number(row['low'], 'effort low'), number(row['high'], 'effort high')
        if low > high or high == 0 or row.get('unit') != 'hours':
            raise ValueError('defensible positive effort range in hours required')
        nonempty(row.get('basis'), 'estimate basis')
        from .policy_features import _evidence_ids
        _evidence_ids(row.get('evidence_ids'), required=True)
        if row.get('basis_kind') != 'accepted_template_estimate':
            raise ValueError('this loader requires an explicitly accepted prototype estimate; measured-duration ingestion is not implemented')
        if 'decision:' + decision['decision_id'] not in row['evidence_ids']:
            raise ValueError('template estimate must cite the real batch decision, not an unrelated source duration')
    templates = copy.deepcopy(batch['milestone_templates'])
    for m in templates:
        m['provenance_class'] = 'policy-derived'
        m['proposal_status'] = 'accepted_by_batch_decision'
        m['derivation_rule_id'] = 'G1AR-ACCEPTED-TEMPLATE-v1'
        m['review'] = {'reviewer_id': decision['reviewer_id'], 'reviewed_at': decision['decided_at'], 'rationale': decision['rationale']}
        m['version'] = 'g1ar-accepted-v1:' + fingerprint({'batch': digest, 'decision': decision})
        m['assessment_instances'] = [r for r in instances if r['criterion_id'] in {c['criterion_id'] for c in m['criteria']}]
        for c in m['criteria']:
            c['anchor_status'] = 'accepted_by_batch_decision'
        for t in m['tasks']:
            e = by_task[t['task_id']]
            t['effort'] = {k: e[k] for k in ('low', 'high', 'unit', 'basis', 'basis_kind', 'evidence_ids')}
            t['effort']['method_id'] = decision['accepted_effort_method_id']
        validate_milestone(m)
    source = {'release_schema_version': 'g1ar-accepted-source-v1', 'batch_sha256': digest,
              'decision': decision, 'decision_sha256': _sha(_path(decision_path)),
              'milestone_templates': templates}
    data = (json.dumps(source, sort_keys=True, indent=2) + '\n').encode()
    release_hash = hashlib.sha256(data).hexdigest()
    relative_path = BASE + '/accepted/' + release_hash + '.json'
    registration = {'source_id': 'g1ar-approved-' + release_hash,
                    'source_version': release_hash, 'source_path': relative_path,
                    'sha256': release_hash, 'provenance_class': 'policy-derived',
                    'role_ids': sorted({m['role_id'] for m in templates})}
    return {'source': source, 'source_bytes': data, 'registration': registration}


def activate_batch(relative=BATCH, *, decision_path):
    """Explicit future activation after a real complete decision; never called by inspect.

    Existing releases are content-addressed and never replaced. Registry changes
    happen only after validation and source publication to the local repository.
    No network, publication outside the repo, scoring, or label writes occur.
    """
    plan = activation_plan(relative, decision_path=decision_path)
    registration = plan['registration']
    path = _path(registration['source_path'])
    registry_path = _path('ml/configs/intelligence/measurement_sources.v1.json')
    registry_bytes = registry_path.read_bytes()
    registry = json.loads(registry_bytes)
    existing = next((r for r in registry['sources'] if r['source_id'] == registration['source_id']), None)
    if existing is not None and existing != registration:
        raise ValueError('conflicting source registration')
    if path.exists() and path.read_bytes() != plan['source_bytes']:
        raise ValueError('immutable source release conflict')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open('xb') as stream:
            stream.write(plan['source_bytes'])
    if existing is None:
        registry['sources'].append(registration)
        temporary = registry_path.with_suffix('.g1ar.tmp')
        try:
            with temporary.open('x') as stream:
                stream.write(json.dumps(registry, indent=2) + '\n')
            if registry_path.read_bytes() != registry_bytes:
                raise ValueError('source registry changed concurrently; retry against current contents')
            temporary.replace(registry_path)
        finally:
            if temporary.exists():
                temporary.unlink()
    return registration


def load_catalogue(*, source_id=None):
    """Default = repaired references only; explicit registered approved release = roles.

    Pending batches are never searched for a best-looking score. A future caller
    selects one exact release source_id after activate_batch was authorized.
    """
    roles = repaired_catalogue()
    if source_id is None:
        return roles
    registry = json.loads(_path('ml/configs/intelligence/measurement_sources.v1.json').read_text())
    registration = next(r for r in registry['sources'] if r['source_id'] == source_id)
    if not source_id.startswith('g1ar-approved-'):
        raise ValueError('select an explicitly approved G1A-R release')
    from .policy_sources import accept_milestone
    source = json.loads(_path(registration['source_path']).read_text())
    if source.get('decision', {}).get('status') != 'approved':
        raise ValueError('release has no approved batch decision')
    by_role = {m['role_id']: m for m in source['milestone_templates']}
    for role in roles:
        raw = by_role[role['role_id']]
        role['milestone'] = accept_milestone(registration['source_path'], registration['sha256'], raw['milestone_id'],
            source_id=source_id, source_version=registration['source_version'], provenance_class='policy-derived')
        role['version'] = 'g1ar-catalogue-v1:' + fingerprint(role)
    return roles
