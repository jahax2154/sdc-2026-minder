"""Offline G1A demonstration. No annotation, training, network or persistent cache."""
import argparse
import json
from .policy import ROOT
from .policy_sources import native_catalogue, accept_milestone
from .inference import recommend_profile


def demonstrate():
    roles = native_catalogue()
    profiles = json.loads((ROOT / 'ml/data/review/phase2/calibration-v1/profiles.synthetic.json').read_text())
    profiles.insert(0, json.loads((ROOT / 'ml/tests/fixtures/phase2_profile.synthetic.json').read_text()))
    actual = [recommend_profile(p, roles) for p in profiles]
    registry = json.loads((ROOT / 'ml/configs/intelligence/measurement_sources.v1.json').read_text())['sources'][0]
    raw = json.loads((ROOT / registry['source_path']).read_text())
    milestone = accept_milestone(registry['source_path'], registry['sha256'], 'synthetic-only',
                                source_id=registry['source_id'], source_version=registry['source_version'],
                                provenance_class=registry['provenance_class'])
    fixture = recommend_profile(raw['profile'], [{'role_id': 'synthetic-role', 'version': 'test-v1', 'milestone': milestone}],
                                answers_by_role={'synthetic-role': raw['answers']})
    exceptions = {}
    for response in actual:
        for derivation in response['derivations']:
            for reason in derivation['exceptions']:
                item = exceptions.setdefault(reason, {'reason': reason, 'affected_profile_ids': set(), 'affected_role_ids': set(),
                    'effect': 'No score for affected pair; catalogue incompleteness is not user inability.',
                    'next_action': 'Supply a source-backed bounded template and explicit version-bound profile measurements.'})
                item['affected_profile_ids'].add(response['profile_id'])
                item['affected_role_ids'].add(derivation['role_id'])
    consolidated = [dict(item, affected_profile_ids=sorted(item['affected_profile_ids']), affected_role_ids=sorted(item['affected_role_ids'])) for item in exceptions.values()]
    consolidated.append({'reason': 'optional_crosswalk_scope_unresolved', 'affected_records': 24,
        'effect': 'Does not block native O*NET identity; cannot support ESCO or Malaysian narrow-role demand.',
        'next_action': 'Resolve 2019 taxonomy versus database-release scope and crosswalk reuse terms before using the bridge.'})
    consolidated.append({'reason': 'independent_labels_absent', 'effect': 'No empirical metrics or learner comparison; policy acceptance is not gold.',
        'next_action': 'Independent blind grading after usable milestone/profile inputs exist; outside G1A.'})
    return {'deduplicated_exceptions': consolidated, 'catalogue_readiness_rule': 'P2-4-policy-acceptance-g1a-v2',
            'historical_checks': 'ml/evaluation/phase2_checks.json',
            'catalogue_readiness': 'partial', 'native_occupations_accepted': len(roles),
            'real_role_milestones_accepted': 0, 'real_pairs_scored': sum(len(r['recommendation']['options']) for r in actual),
            'meaningful_baseline_data_gate': 'blocked', 'empirical_readiness': 'not_evaluated_no_independent_labels',
            'live_service_readiness': {'python_callable': 'exercised', 'http_endpoint': 'not_implemented', 'frontend': 'not_implemented'},
            'actual_profiles': actual, 'synthetic_contract_fixture_only': fixture,
            'accepted_native_projection': roles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(demonstrate(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
