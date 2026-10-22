"""Reproducible local catalogue/service evidence; synthetic examples are not labels.

Run: python -m minder_ml.intelligence.personal_cli --output <lane-artifact-dir>
No network, credentials, training, database writes or policy activation.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from .catalogue_service import OccupationalCatalogue
from .personal_service import PersonalMatchingService
from .policy import ROOT
from .service_contracts import validate


def synthetic_profile(audience='student'):
    fixture = json.loads((ROOT / 'contracts/fixtures/parallel-v1/complete_profile.json').read_text())['payload']
    profile = copy.deepcopy(fixture)
    profile.update(profile_id='demo-' + audience, profile_group_id='demo-' + audience,
                   version='personal-demo-v1', preferences=[])
    profile['evidence'][0].update(subject_id='onet:element:2.A.1.a',
                                  method_id='synthetic-demonstration-not-accepted-rubric')
    if audience not in ('student', 'fresh_graduate'):
        profile['current_fields'] = [dict(field_id='synthetic:prior-industry', field_type='industry',
                                          state='want_to_leave' if audience == 'career_switcher' else 'known',
                                          evidence_ids=[])]
    return validate('Profile', profile)


def adapt_original_profile(profile, source_bytes):
    """Lossless evidence values only: do not map draft skills to source skills.

    The original document is hash-bound; unsupported free text remains a claim,
    not a competence rating. This evidence adapter is for coverage comparison.
    """
    source = dict(source_id='existing-synthetic-calibration', version=profile['version'],
                  sha256=hashlib.sha256(source_bytes).hexdigest(),
                  uri='repo:ml/data/review/phase2/calibration-v1/profiles.synthetic.json',
                  geography='synthetic', available_at='2026-10-23T00:00:00Z',
                  evidence_type='synthetic-fixture')
    evidence = []
    for i, observation in enumerate(profile['skill_observations']):
        value = observation['demonstrated_fraction']
        evidence.append(dict(evidence_id=f"{profile['profile_id']}:skill:{i}",
                             subject_id=observation['skill_id'], value=value,
                             state='unknown' if value is None else 'known', unit='fraction_0_1',
                             provenance=source, method_id='legacy-state:' + observation['state']))
    for field in ('interests', 'work_preferences', 'projects_achievements', 'education_experience', 'career_goal'):
        evidence.append(dict(evidence_id=f"{profile['profile_id']}:{field}",
                             subject_id='legacy-claim:' + field,
                             value=json.dumps(profile.get(field), sort_keys=True), state='known',
                             unit='source_claim_json', provenance=source, method_id='unmapped-claim-not-competence'))
    return validate('Profile', dict(
        profile_id=profile['profile_id'], profile_group_id=profile['profile_family_id'],
        version=profile['version'], synthetic=True, evidence=evidence, preferences=[],
        current_fields=[dict(field_id='unknown', field_type='industry', state='unknown', evidence_ids=[])],
        constraints=[], timezone='Asia/Kuala_Lumpur'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    allowed = (ROOT / 'ml/artifacts/session-a').resolve()
    if not output.is_relative_to(allowed):
        raise ValueError('write service evidence only under Session A artifacts')
    output.mkdir(parents=True, exist_ok=False)
    catalogue = OccupationalCatalogue()
    service = PersonalMatchingService()
    path = ROOT / 'ml/data/review/phase2/calibration-v1/profiles.synthetic.json'
    raw = path.read_bytes()
    original = json.loads(raw)
    # Reuse the unchanged actual legacy service to observe before coverage.
    from .catalogue_repair import repaired_catalogue
    from .inference import recommend_profile
    legacy_roles = repaired_catalogue()
    summary = dict(catalogue=catalogue.coverage, original_profiles=[], synthetic_demonstrations=[],
                   notice='All profiles synthetic; unknowns preserved. No empirical validity or numeric N01 score.')
    roles = catalogue.roles()
    for old in original:
        before = recommend_profile(old, legacy_roles)
        result = service.assess(adapt_original_profile(old, raw), roles)
        row = dict(profile_id=old['profile_id'], original_sha256=hashlib.sha256(raw).hexdigest(),
                   legacy_runtime_roles=len(legacy_roles), legacy_scored=len(before['recommendation']['options']),
                   new_runtime_roles=len(roles), new_candidates=len(result['public']['candidate_ids']),
                   new_scored=sum(r['score'] is not None for r in result['internal']['personal_assessments']),
                   status=result['public']['status'])
        summary['original_profiles'].append(row)
        (output / (old['profile_id'] + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    for audience in ('student', 'fresh_graduate', 'career_switcher', 'uncertain_worker', 'displaced_worker'):
        profile = synthetic_profile(audience)
        result = service.assess(profile, roles)
        summary['synthetic_demonstrations'].append(dict(
            audience=audience, profile_id=profile['profile_id'],
            supplied_evidence='known synthetic skill fraction, no accepted comparison rubric',
            candidates=len(result['public']['candidate_ids']), scores=0,
            status=result['public']['status']))
        (output / (profile['profile_id'] + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    (output / 'coverage.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'catalogue'}, indent=2))


if __name__ == '__main__':
    main()
