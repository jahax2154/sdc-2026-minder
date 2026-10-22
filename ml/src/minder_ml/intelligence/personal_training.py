"""Reusable bounded learner machinery, strictly separated from pending role fit.

Reuses actual Ridge/StandardScaler and CPU XGBoost implementations. Only the
named mathematical fixture may fit locally, as authorised by the execution pack.
Empirical role-fit training remains blocked by N01, target labels and rubrics;
paid execution is B-only. No function in this module promotes a live model.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

from .policy import ROOT, fingerprint
from .artifacts import fit_timed, predict_raw, versions, digest
from .estimators import make_estimator, configure_threads

CONFIG = ROOT / 'ml/configs/intelligence/personal-machinery.v1.json'
ARTIFACT_ROOT = ROOT / 'ml/artifacts/session-a'
TARGET = 'synthetic_math_only'


def label_inventory():
    """Observe actual labels; never migrate preparation judgments to role fit."""
    from .evaluation import read_annotations
    path = ROOT / 'ml/data/annotations/personal_fit_annotations.csv'
    _, existing = read_annotations(path)
    pending = ROOT / 'ml/data/review/annotation_intake.pending.csv'
    with pending.open(newline='') as stream:
        provisional = list(csv.DictReader(stream))
    return dict(legacy_annotation_path=str(path.relative_to(ROOT)), sha256=digest(path),
                legacy_annotation_report=existing, intake_rows=len(provisional),
                compatible_initial_role_fit_labels=0,
                target_migration='No accepted role-fit target/rubric; legacy milestone grades are incompatible.',
                status='blocked_decision', blockers=['N01', 'compatible_target_and_evidence_rubric'],
                human_review_notice='Independent review is not a launch prerequisite; generated labels remain provisional.')


def grouped_split(rows, *, seed=42):
    """Freeze profile-family groups before preprocessing/fitting; reject leakage."""
    groups = sorted({r['profile_group_id'] for r in rows})
    if len(groups) < 4:
        raise ValueError('at least four groups required for this smoke split')
    profiles, vectors = {}, {}
    for row in rows:
        pid, gid = row['profile_id'], row['profile_group_id']
        if pid in profiles and profiles[pid] != gid:
            raise ValueError('profile occurs in multiple groups')
        profiles[pid] = gid
        vector = tuple(row['x'])
        if vector in vectors and vectors[vector] != gid:
            raise ValueError('duplicate feature vector crosses groups')
        vectors[vector] = gid
    random.Random(seed).shuffle(groups)
    n_holdout = max(1, len(groups) // 4)
    return dict(seed=seed, development=sorted(groups[n_holdout:]), holdout=sorted(groups[:n_holdout]),
                method='group-disjoint deterministic shuffle; synthetic control only',
                preprocessing_fit='development only', holdout_used_for_selection=False)


def machinery_plan():
    config = json.loads(CONFIG.read_text())
    path = (ROOT / config['fixture_path']).resolve()
    if not path.is_relative_to(ROOT) or digest(path) != config['fixture_sha256']:
        raise ValueError('pinned mathematical fixture mismatch')
    fixture = json.loads(path.read_text())
    if fixture['data_kind'] != TARGET or config['target'] != TARGET or config['promotable'] is not False:
        raise ValueError('only non-promotable synthetic mathematical smoke is allowed locally')
    x, y = fixture['x'], fixture['y']
    if not x or len(x) != len(y) or len(x) > 64:
        raise ValueError('invalid bounded smoke shape')
    rows = []
    for i, (features, target) in enumerate(zip(x, y)):
        if (len(features) != config['feature_count']
                or any(isinstance(v, bool) or not isinstance(v, (int, float))
                       or not math.isfinite(v) for v in features + [target])):
            raise ValueError('invalid mathematical features/target')
        rows.append(dict(profile_id='math-row-' + str(i), profile_group_id='math-family-' + str(i // 2),
                         x=features, y=target))
    split = grouped_split(rows)
    return dict(manifest_version='personal-learner-machinery-v1', target=TARGET,
                provenance='deterministic mathematical fixture; not personal-fit labels',
                promotable=False, policy_id=None, feature_schema=config['feature_schema'],
                dataset_path=config['fixture_path'], dataset_sha256=digest(path),
                split=split, split_sha256=fingerprint(split), rows=rows,
                methods=['baseline', 'ridge', 'xgboost'],
                baseline='train-only constant-mean mathematical control; not a personal-fit formula',
                estimators='existing estimators.make_estimator, ridge_l2=1; fixed parameters, no tuning',
                execution=config['execution'], budget_usd=0,
                empirical_personal_fit=label_inventory())


def _controlled(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ARTIFACT_ROOT.resolve()):
        raise ValueError('learner output must stay under Session A artifacts')
    return path


def load_machinery_candidate(run, kind, *, expected_target, expected_feature_schema):
    """Trusted local artifacts only. All semantic checks occur before joblib load."""
    run = _controlled(run)
    meta = json.loads((run / 'metadata.json').read_text())
    if expected_target != TARGET or meta['target'] != expected_target or meta['promotable'] is not False:
        raise ValueError('target incompatible: mathematical controls cannot serve personal role fit')
    if meta['feature_schema'] != expected_feature_schema or meta['package_versions'] != versions():
        raise ValueError('incompatible feature schema or package versions')
    if kind not in ('baseline', 'ridge', 'xgboost'):
        raise ValueError('unknown candidate')
    if meta['implementation_hashes'] != {p.name: digest(p) for p in (Path(__file__), Path(__file__).with_name('estimators.py'))}:
        raise ValueError('implementation changed; compatibility review required')
    path = run / kind / 'pipeline.joblib'
    if path.is_symlink() or not path.resolve().is_relative_to(run) or digest(path) != meta['candidates'][kind]['sha256']:
        raise ValueError('pipeline integrity mismatch')
    import joblib
    from sklearn.utils.validation import check_is_fitted
    model = joblib.load(path)
    check_is_fitted(model)
    if model.n_features_in_ != len(expected_feature_schema['names']):
        raise ValueError('artifact feature count mismatch')
    return model


def run_machinery(output):
    """Actual same-holdout baseline/Ridge/boosting fit/save/reload/predict smoke."""
    plan = machinery_plan()  # guard all inputs before any fit/output
    output = _controlled(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'manifest.json').write_text(json.dumps(plan, indent=2) + '\n')
    development = [r for r in plan['rows'] if r['profile_group_id'] in plan['split']['development']]
    holdout = [r for r in plan['rows'] if r['profile_group_id'] in plan['split']['holdout']]
    x, y = [r['x'] for r in development], [r['y'] for r in development]
    hx, hy = [r['x'] for r in holdout], [r['y'] for r in holdout]
    configure_threads()
    import joblib
    from sklearn.dummy import DummyRegressor
    meta = dict(target=TARGET, promotable=False, feature_schema=plan['feature_schema'],
                package_versions=versions(), execution_location='local_cpu_smoke',
                implementation_hashes={p.name: digest(p) for p in (Path(__file__), Path(__file__).with_name('estimators.py'))},
                dataset_sha256=plan['dataset_sha256'], split_sha256=plan['split_sha256'],
                candidates={})
    models, report = {}, dict(status='synthetic_machinery_only', empirical_personal_fit='not_evaluated',
                              development_rows=len(x), holdout_rows=len(hx), candidates={},
                              selected_personal_model=None, active_personal_model=None,
                              live_selection='none: N01 and compatible labels absent')
    for kind in plan['methods']:
        model = DummyRegressor(strategy='mean') if kind == 'baseline' else make_estimator(kind)
        timing = fit_timed(model, x, y)
        folder = output / kind
        folder.mkdir()
        path = folder / 'pipeline.joblib'
        joblib.dump(model, path)
        meta['candidates'][kind] = dict(sha256=digest(path), timing=timing)
        models[kind] = model
    (output / 'metadata.json').write_text(json.dumps(meta, indent=2, allow_nan=False) + '\n')
    for kind, model in models.items():
        restored = load_machinery_candidate(output, kind, expected_target=TARGET,
                                              expected_feature_schema=plan['feature_schema'])
        before, after = predict_raw(model, hx), predict_raw(restored, hx)
        if len(after) != len(hy) or not all(math.isfinite(v) for v in before + after):
            raise ValueError('invalid prediction shape or value')
        delta = max(abs(a - b) for a, b in zip(before, after))
        if delta > 1e-9:
            raise ValueError('prediction changed on reload')
        report['candidates'][kind] = dict(
            fit='succeeded', evaluated='mathematical holdout only', selected=False, active=False,
            reload_max_absolute_difference=delta,
            mae=sum(abs(p - t) for p, t in zip(after, hy)) / len(hy),
            rmse=math.sqrt(sum((p - t) ** 2 for p, t in zip(after, hy)) / len(hy)),
            predictions=after, pipeline_sha256=meta['candidates'][kind]['sha256'])
    (output / 'metrics.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'smoke'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'plan':
        output = _controlled(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream:
            json.dump(machinery_plan(), stream, indent=2)
        print(json.dumps(label_inventory(), indent=2))
    else:
        print(json.dumps(run_machinery(args.output), indent=2))


if __name__ == '__main__':
    main()
