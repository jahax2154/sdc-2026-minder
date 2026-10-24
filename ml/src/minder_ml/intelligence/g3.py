"""G3 inventory/evaluation report. Fits remain in the guarded existing training CLI."""
from collections import Counter
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from .policy import ROOT, load_policy
from .data_pipeline import parse_dosm
from .market_indexes import build_indexes
from .catalogue_repair import load_catalogue, load_batch
from .evaluation import read_annotations
from .training import evaluate_baseline, compare, smoke
from .estimators import make_estimator, THREADS
from . import artifacts


def runner_readiness():
    # Only presence/name inspection; never serialize credentials or their values.
    env_names = sorted(k for k in os.environ if k.startswith('RUNPOD'))
    env_files = []
    configured_names = set(env_names)
    for relative in ('.env', '.env.local', 'ml/.env', 'ml/.env.local'):
        path = ROOT / relative
        if path.is_file():
            env_files.append(relative)
            for line in path.read_text().splitlines():
                key = line.partition('=')[0].strip().removeprefix('export ')
                if key.startswith('RUNPOD'):
                    configured_names.add(key)
    return {'status': 'not_verified', 'runpod_variable_names_only': sorted(configured_names),
            'env_files_present': env_files, 'runpod_cli_present': shutil.which('runpodctl') is not None,
            'runpod_config_present': any((Path.home()/p).exists() for p in ('.runpod', '.config/runpod')),
            'ssh_config_present': (Path.home()/'.ssh/config').is_file(),
            'pod_target': None, 'credit_applicability': None, 'available_balance': None, 'agreed_budget': None,
            'reason': 'No verified funded CPU runner attestation supplied; presence alone would not establish credit or spending authorization.'}


def coverage(rows, quality, provenance):
    roles = load_catalogue()
    batch = load_batch()
    profiles = [json.loads((ROOT/'ml/tests/fixtures/phase2_profile.synthetic.json').read_text())]
    profiles += json.loads((ROOT/'ml/data/review/phase2/calibration-v1/profiles.synthetic.json').read_text())
    accepted, labels = read_annotations(ROOT/'ml/data/annotations/personal_fit_annotations.csv')
    manifest = json.loads((ROOT/'ml/minder_ml_starter/sources_manifest.json').read_text())
    source_inventory = []
    for source in manifest['sources']:
        path = ROOT/'ml/minder_ml_starter'/source['relative_path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        source_inventory.append({'source_id': source['id'], 'scope': source.get('scope'),
            'version': source.get('documented_version') or source.get('documented_as_of'),
            'sha256': actual, 'manifest_hash_matches': actual == source.get('sha256'),
            'unit': source.get('units'), 'license': source.get('license'), 'is_user_role_label_source': False})
    profile_rows = []
    for p in profiles:
        profile_rows.append({'profile_id': p['profile_id'], 'profile_family_id': p['profile_family_id'],
            'profile_version': p['version'], 'data_class': p['data_class'],
            'country_region': p['country_region_preference'], 'hours_per_week': p['hours_per_week'],
            'horizon_weeks': p['planning_horizon']['weeks'], 'career_goal': p['career_goal'],
            'education_experience': p['education_experience'],
            'resources_and_constraints': p['access_budget_constraints'],
            'interests': p['interests'], 'work_preferences': p['work_preferences'],
            'skill_evidence_states': dict(Counter(o['state'] for o in p['skill_observations'])),
            'independent_label_count': sum(r['profile_id'] == p['profile_id'] for r in accepted)})
    criteria = []
    for role in roles:
        for c in role['pending_criteria']:
            observations = [o for p in profiles for o in p['skill_observations']
                            if o.get('criterion_id') == c['criterion_id'] and o.get('role_id') == role['role_id']]
            criteria.append({'role_id': role['role_id'], 'role_version': role['version'],
                'criterion_id': c['criterion_id'], 'source_skill_id': c['skill_id'],
                'milestone_id': None, 'milestone_status': 'pending_batch_decision',
                'anchored_known_profile_assessments': sum(o.get('demonstrated_fraction') is not None for o in observations),
                'candidate_profile_pairs': len(profiles), 'accepted_milestone': False})
    dimensions = []
    for name in sorted({r['dimension_scope'] for r in rows}):
        subset = [r for r in rows if r['dimension_scope'] == name]
        dimensions.append({'dimension': name, 'rows': len(subset),
            'numeric': sum(r['value'] is not None for r in subset),
            'missing': sum(r['value'] is None for r in subset),
            'published_entity_labels': sorted({r['occupation_label'] or r['industry_label'] for r in subset}),
            'geographies': sorted({r['geography_code'] for r in subset}),
            'periods': sorted({r['period_start'] for r in subset}),
            'measurement_grain': 'country × quarter × source-native published marginal label',
            'evidence_type': 'observed provider aggregate; not independent personal-fit labels'})
    return {'coverage_schema_version': 'minder-coverage-g3-v1', 'source_inventory': source_inventory,
        'source_checks': provenance['checksums'], 'market_quality': quality,
        'market_dimensions': dimensions, 'criterion_coverage': criteria,
        'profile_circumstances': profile_rows,
        'family_counts': {'distinct_declared_synthetic_family_ids': len({p['profile_family_id'] for p in profiles}),
                          'independently_labeled_groups': len({r['profile_group_id'] for r in accepted}),
                          'notice': 'Distinct synthetic family IDs do not establish independent reviewer evidence.'},
        'independent_label_report': labels,
        'data_modes': {'synthetic_math_fixture': '32 continuous mathematical controls, not rubric labels',
            'policy_distillation': 'not_run_no_G1B_proposal_targets_supplied',
            'independent_empirical': 'not_evaluated_no_eligible_independent_labels'},
        'pending_template_count': len(batch['milestone_templates']),
        'top_missing_slices': [
            {'factor': 'Accepted bounded milestones, estimates and anchored profile measurements', 'decision_affected': 'Whether any of the 18 actual profile-role pairs can receive F.'},
            {'factor': 'Compatible independent user-role labels spanning profile families', 'decision_affected': 'Whether Ridge/XGBoost quality can be compared and a candidate recommended.'},
            {'factor': 'Fine-grained Malaysian role demand with defensible occupation mappings', 'decision_affected': 'Whether D and combined S can be shown for the actual three O*NET roles.'},
            {'factor': 'Skill-tagged and employer-resolved observed activity', 'decision_affected': 'Whether skill demand/employer views can contain measured counts or indexes.'},
            {'factor': 'Industry continuity at 2026-Q2 and observed joint/regional/international slices', 'decision_affected': 'Whether industry YoY/current indexes or cross-slice comparisons are defensible.'}]}


def inspect_gate():
    rows, quality, provenance = parse_dosm()
    inventory = coverage(rows, quality, provenance)
    indexes = build_indexes(rows)
    preflight = {'versions': artifacts.versions(), 'thread_limit': THREADS, 'fitting_performed': False, 'estimators': {}}
    for kind in ('ridge', 'xgboost'):
        try:
            model = make_estimator(kind)
            preflight['estimators'][kind] = {'construction': 'passed', 'steps': list(model.named_steps),
                'estimator_settings': {k: str(v) for k, v in model.get_params().items() if k.startswith('estimator__')}}
        except (OSError, ImportError, ValueError) as exc:
            preflight['estimators'][kind] = {'construction': 'failed', 'error_type': type(exc).__name__}
    data_path = ROOT/'ml/data/annotations/personal_fit_annotations.csv'
    baseline = evaluate_baseline(data_path, 'g3-independent-baseline')
    comparison = compare(data_path, 'g3-independent-comparison', None)
    try:
        smoke('g3-synthetic-machinery', ROOT/'ml/tests/fixtures/synthetic_math.json', None)
    except ValueError as exc:
        smoke_status = {'status': 'blocked', 'reason': str(exc), 'fitting_performed': False,
                        'reload_parity': 'not_measured', 'actual_execution_location': 'local preflight only'}
    else:
        raise RuntimeError('unverified fitting unexpectedly ran')
    return {'gate': 'G3', 'coverage': inventory, 'market_indexes': indexes, 'cpu_preflight': preflight,
        'runpod': runner_readiness(), 'cpu_fit_predict_save_reload': smoke_status,
        'independent_baseline_evaluation': baseline, 'independent_comparison': comparison,
        'policy_distillation': {'status': 'not_run', 'reason': 'No compatible G1B proposals found; optional experiment not synthesized from independent labels.'},
        'selection': {'active': 'baseline', 'recommended': 'baseline', 'reason': 'No independent comparison evidence justifies a learner; no model switched.'},
        'G2': {'existing_interface_preserved': True, 'completion_report_found': any((ROOT/'docs/execution/gates').glob('G2*report.md')),
               'live_chat_exercised': False, 'reason': 'Only a task document and application scaffolding were found.'}}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(inspect_gate(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
