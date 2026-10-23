"""Pinned native-source projections; no generated task becomes a source fact."""
import csv
import hashlib
import json
from .policy import ROOT, fingerprint, load_policy


def role_reference_v3():
    """Pinned native anchors/industry/work-style projection, not personal labels."""
    config = json.loads((ROOT / 'ml/configs/intelligence/personal-role-fit.v3.json').read_text())
    path = (ROOT / config['reference_path']).resolve()
    if not path.is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != config['reference_sha256']:
        raise ValueError('role reference v3 checksum/path mismatch')
    data = json.loads(path.read_text())
    if data['version'] != 'role-reference-v3.1':
        raise ValueError('role reference version mismatch')
    return data


def native_catalogue():
    _, active = load_policy()
    pack = ROOT / 'ml/minder_ml_starter'
    manifest = json.loads((pack / 'sources_manifest.json').read_text())
    records, refs = {}, {}
    for sid in ('onet_occupation_data', 'onet_essential_skills'):
        entry = next(s for s in manifest['sources'] if s['id'] == sid)
        if entry.get('documented_version') != '31.0':
            raise ValueError('database release mismatch: ' + sid)
        path = pack / entry['relative_path']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise ValueError('source hash mismatch: ' + sid)
        with path.open(newline='', encoding='utf-8-sig') as stream:
            records[sid] = list(csv.DictReader(stream))
        refs[sid] = {'source_id': sid, 'sha256': digest, 'database_version': '31.0',
                     'path': str(path.relative_to(ROOT)), 'url': entry['url'],
                     'license': entry['license'], 'scope': entry['scope']}
    drafts = json.loads((ROOT / 'ml/data/review/phase2/roles.pending.json').read_text())
    roles = []
    for draft in drafts:
        code = draft['role_id']
        matches = [r for r in records['onet_occupation_data'] if r['O*NET-SOC Code'] == code]
        if len(matches) != 1 or matches[0]['Title'] != draft['title']:
            raise ValueError('native occupation identity mismatch: ' + code)
        skills = [dict(r, evidence_id='onet31:skills:' + str(i + 2))
                  for i, r in enumerate(records['onet_essential_skills'])
                  if r['O*NET-SOC Code'] == code]
        role = {'role_id': code, 'title': matches[0]['Title'],
                'occupation_reference': matches[0], 'occupation_skills': skills,
                'identifier': {'system': 'O*NET-SOC', 'code': code,
                               'taxonomy_edition': None, 'database_version': '31.0'},
                'status': 'policy_accepted', 'provenance_class': 'source-derived',
                'rule_ids': ['AUTO-01', 'FIT-02'], 'sources': list(refs.values()),
                'milestone': None, 'pending_criteria': draft['criteria'],
                'original_draft_path': 'ml/data/review/phase2/roles.pending.json',
                'optional_crosswalk_status': 'quarantined_not_needed_for_native_identity',
                'original_draft_version': draft['version'],
                'milestone_exception': 'Draft task criteria have no content anchors, task DAG, effort basis, interest/resource/work-style definitions.',
                'policy': active}
        role['version'] = 'native-g1a-v1:' + fingerprint(role)
        roles.append(role)
    return roles


def accept_milestone(source_path, expected_sha256, record_id, *, source_id, source_version,
                     provenance_class='source-derived'):
    """Project an explicitly pinned structured milestone template, never prose extraction.

    Caller supplies an accepted source manifest, not a status flag on a role draft.
    Templates need explicit preparation scope and all FIT inputs. Generated proposals
    are rejected even when their files have valid hashes.
    """
    from .policy_features import validate_milestone
    if provenance_class not in ('source-derived', 'policy-derived', 'human-reviewed'):
        raise ValueError('provisional judgments cannot be auto-accepted')
    if not source_id or not source_version:
        raise ValueError('source identity and actual version required')
    registry = json.loads((ROOT / 'ml/configs/intelligence/measurement_sources.v1.json').read_text())
    registered = next((r for r in registry['sources'] if r['source_id'] == source_id), None)
    if not registered or any(registered.get(k) != v for k, v in {
            'source_path': source_path, 'source_version': source_version,
            'sha256': expected_sha256, 'provenance_class': provenance_class}.items()):
        raise ValueError('source is not a registered structured milestone source')
    path = ROOT / source_path
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError('source outside repository')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('source hash mismatch')
    raw = json.loads(path.read_text())
    record = next(r for r in raw['milestone_templates'] if r['milestone_id'] == record_id)
    if record.get('provenance_class') != provenance_class:
        raise ValueError('source provenance mismatch')
    if provenance_class == 'policy-derived' and not record.get('derivation_rule_id'):
        raise ValueError('policy derivation rule required')
    if provenance_class == 'human-reviewed' and not all(record.get('review', {}).get(k)
            for k in ('reviewer_id', 'reviewed_at', 'rationale')):
        raise ValueError('actual human review attestation required')
    if record.get('role_id') not in registered['role_ids']:
        raise ValueError('template role outside registered source scope')
    validate_milestone(record)
    return dict(record, status='policy_accepted', acceptance={
        'source_id': source_id, 'source_version': source_version,
        'sha256': expected_sha256, 'record_id': record_id,
        'record_sha256': fingerprint(record), 'source_path': source_path,
        'rule_id': 'AUTO-01'})


def verify_milestone_acceptance(milestone):
    """Revalidate content-addressed acceptance, not a caller-provided status alone."""
    proof = milestone.get('acceptance', {})
    accepted = accept_milestone(proof['source_path'], proof['sha256'], proof['record_id'],
                                source_id=proof['source_id'], source_version=proof['source_version'],
                                provenance_class=milestone['provenance_class'])
    if accepted != milestone:
        raise ValueError('accepted milestone content changed; re-project its pinned source')
    return True
