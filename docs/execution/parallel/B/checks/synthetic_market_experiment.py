"""Isolated fictional count scenarios. Never an observed-data or serving runner."""
import argparse
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import random
import importlib.metadata
import resource
import subprocess
import sys
import time

import joblib

from minder_ml.intelligence.data_pipeline import MARKET_DATA, MARKET_ARTIFACTS, sha
from minder_ml.intelligence.forecasting import feature_vector, history_as_of, quarter_number
from minder_ml.intelligence.service_contracts import next_calendar_quarter

VERSION = 'fictional-market-scenarios-v1'
LABEL = 'Simulated scenario — generated assumptions, not observed Malaysian demand.'
SCENARIOS = ('stable', 'rising', 'falling', 'seasonal', 'abrupt', 'sparse', 'missing', 'coverage_change')
SPEC = MARKET_DATA / 'synthetic-lab/scenario-spec.v1.json'
DEFAULT_OUTPUT = MARKET_ARTIFACTS / 'synthetic-lab/v1'


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + '\n')


def observed_hashes(source_root=None):
    # Includes the unchanged normal registry, original inputs and all market data
    # except the explicitly isolated lab specification namespace.
    paths = [p for p in MARKET_DATA.rglob('*') if p.is_file() and 'synthetic-lab' not in p.parts]
    manifest = json.loads(Path('docs/execution/parallel/source_snapshot.v1.json').read_text())
    source_root = Path('ml/minder_ml_starter') if source_root is None else Path(source_root)
    paths += [source_root / r['path'] for r in manifest['source_files']]
    # A clean RunPod code checkout must not require uploading preserved raw
    # source records merely to run fully fictional simulations. Absence is
    # explicit and also checked for changes; existing local inputs stay pinned.
    return {str(p): sha(p) if p.is_file() else 'absent_not_required_for_simulation'
            for p in sorted(paths)}


def generate(spec):
    if spec['generator'] != VERSION or spec['synthetic'] is not True:
        raise ValueError('explicit_synthetic_spec_required')
    # Assign source/scenario groups before drawing any random values. No fitted
    # generator, real anchors, source records, profiles or LLM labels are used.
    family_splits = {'stable': 'train', 'rising': 'train', 'falling': 'train',
                     'seasonal': 'validation', 'sparse': 'validation',
                     'abrupt': 'test', 'missing': 'test', 'coverage_change': 'test'}
    assignments = [(s, family_splits[s], f'sim:{s}') for s in SCENARIOS]
    assignments += [('damped_cycle', 'robustness', 'sim:damped_cycle:robustness')]
    rows, groups = [], []
    for index, (scenario, split, group) in enumerate(assignments):
        rng = random.Random(spec['seed'] + index)
        scale = rng.uniform(.85, 1.15)
        groups.append({'group_id': group, 'scenario': scenario, 'split': split,
                       'seed': spec['seed'] + index, 'scale': scale,
                       'relationship': 'skill count is rounded ~55% of role count plus bounded fictional noise; same group'})
        for i in range(spec['quarters']):
            start = date(2010 + i // 4, 1 + 3 * (i % 4), 1)
            following = date(start.year + 1, 1, 1) if start.month == 10 else date(start.year, start.month + 3, 1)
            end = following - timedelta(days=1)
            base = {'stable': 80, 'rising': 10 + 2*i + 3*(i % 4),
                    'falling': max(5, 130 - 2*i),
                    'seasonal': 80 + (0, 30, 0, -30)[i % 4],
                    'abrupt': 65 if i < 32 else 145,
                    'sparse': 0 if i % 4 != 0 else 12,
                    'missing': 70 + i,
                    'coverage_change': 75 if i < 28 else 150,
                    'damped_cycle': 80 + 35*math.exp(-i/35)*math.sin(i*math.pi/6)}[scenario]
            role = max(0, round(scale * base + (rng.randint(-2, 2) if base else 0)))
            skill = min(role, max(0, round(.55 * role + rng.randint(-1, 1))))
            missing = scenario == 'missing' and i in (9, 21, 34, 43)
            epoch = int(scenario == 'coverage_change' and i >= 28)
            for family, value in (('role', role), ('skill', skill)):
                rows.append({'synthetic': True, 'display_label': LABEL, 'dataset_id': VERSION,
                             'geography': 'SIMULATED', 'entity_type': family,
                             'entity_id': group + ':' + family, 'group_id': group,
                             'scenario': scenario, 'split': split,
                             'source_universe_id': group + ':coverage-' + str(epoch),
                             'simulated_denominator': 1000 * (1 + epoch),
                             'period': {'start': start.isoformat(), 'end': end.isoformat()},
                             'published_at': (end + timedelta(days=20)).isoformat() + 'T00:00:00Z',
                             'available_at': (end + timedelta(days=20)).isoformat() + 'T00:00:00Z',
                             'unit': 'fictional advertisement counts', 'collection_complete': not missing,
                             'value': None if missing else value})
    return {'version': VERSION, 'synthetic': True, 'display_label': LABEL,
            'normal_serving_eligible': False, 'real_aggregate_anchors': [],
            'spec_sha256': sha(SPEC), 'groups': groups, 'rows': rows}


def examples(dataset):
    if dataset.get('synthetic') is not True:
        raise ValueError('lab_requires_synthetic_data')
    by_series = {}
    for row in dataset['rows']:
        if row['synthetic'] is not True or row['geography'] != 'SIMULATED':
            raise ValueError('mixed_or_observed_data_forbidden')
        by_series.setdefault((row['entity_id'], row['source_universe_id']), []).append(row)
    result, excluded = [], Counter()
    for rows in by_series.values():
        for origin in rows:
            issue = origin['available_at']
            target = next_calendar_quarter(issue)
            labels = [r for r in rows if r['period'] == target]
            if not labels:
                excluded['no_target_in_same_coverage_epoch'] += 1
                continue
            label = labels[0]
            if label['value'] is None:
                excluded['missing_target_not_zero'] += 1
                continue
            history = history_as_of(rows, issue)
            try:
                x = feature_vector(history, target)
            except ValueError as exc:
                excluded[str(exc)] += 1
                continue
            seasonal = [r for r in history if quarter_number(r['period']['start']) == quarter_number(target['start']) - 4]
            if not seasonal or seasonal[-1]['value'] is None:
                excluded['seasonal_unavailable_common_comparison'] += 1
                continue
            split = label['split']
            # Disjoint groups AND time, with publication embargoes at boundaries.
            eligible = ((split == 'train' and label['available_at'] < '2018-01-01') or
                        (split == 'validation' and '2018-01-01' <= issue < '2020-01-01'
                         and label['available_at'] < '2020-01-01') or
                        (split in ('test', 'robustness') and issue >= '2020-01-01'))
            if not eligible:
                excluded['outside_prespecified_group_time_split'] += 1
                continue
            result.append({'synthetic': True, 'example_id': hashlib.sha256(
                (label['entity_id'] + issue).encode()).hexdigest(),
                'group_id': label['group_id'], 'scenario': label['scenario'],
                'entity_type': label['entity_type'], 'issued_at': issue,
                'target_period': target, 'label_available_at': label['available_at'],
                'split': split, 'x': x, 'x_news': None, 'label': label['value'],
                'no_change': history[-1]['value'], 'seasonal': seasonal[-1]['value'],
                'history_periods': [r['period'] for r in history[-4:]],
                'history_available_at': [r['available_at'] for r in history[-4:]],
                'source_universe_id': label['source_universe_id']})
    group_sets = {s: {e['group_id'] for e in result if e['split'] == s}
                  for s in ('train', 'validation', 'test', 'robustness')}
    assert all(not group_sets[a] & group_sets[b] for a in group_sets for b in group_sets if a != b)
    assert all(all(t <= e['issued_at'] for t in e['history_available_at']) for e in result)
    assert all(e['x'][-1] == 2 for e in result)
    return result, dict(excluded)


def isolation(dataset, output):
    from minder_ml.intelligence.market_training import experiment
    from minder_ml.intelligence.market_service import MarketEvidenceService
    from minder_ml.intelligence.forecasting import ForecastRegistry
    checks = {}
    for name, call in (
        ('observed_training_runner', lambda: experiment(dataset, evaluation_as_of='2023-01-01T00:00:00Z', output_dir=output)),
        ('normal_market_service', lambda: MarketEvidenceService(snapshot=dataset)),
    ):
        try:
            call()
        except ValueError as exc:
            assert 'synthetic' in str(exc) or 'explicitly real evidence' in str(exc)
            checks[name] = str(exc)
        else:
            raise AssertionError(name + ' accepted synthetic data')
    path = output / 'synthetic-serving-denied.json'
    registry = json.loads((MARKET_DATA / 'serving-registry.v1.json').read_text())
    registry.update(synthetic=True, normal_serving_eligible=False)
    write(path, registry)
    try:
        ForecastRegistry(path)
    except ValueError as exc:
        assert 'synthetic' in str(exc)
        checks['normal_registry'] = str(exc)
    else:
        raise AssertionError('synthetic registry accepted')
    assert ForecastRegistry().manifest['models'] == []
    return checks


def prepare(output):
    before = observed_hashes()
    dataset = generate(json.loads(SPEC.read_text()))
    assert dataset == generate(json.loads(SPEC.read_text()))
    write(output / 'dataset.json', dataset)
    prepared, excluded = examples(dataset)
    write(output / 'examples.json', {'synthetic': True, 'examples': prepared, 'excluded': excluded})
    checks = isolation(dataset, output)
    assert observed_hashes() == before
    result = {'synthetic': True, 'normal_serving_eligible': False, 'generator': VERSION,
              'dataset_sha256': sha(output / 'dataset.json'), 'spec_sha256': sha(SPEC),
              'generator_sha256': sha(Path(__file__)), 'records': len(dataset['rows']),
              'groups': len(dataset['groups']), 'series': len(dataset['groups'])*2,
              'example_splits': dict(Counter(e['split'] for e in prepared)),
              'missing_values': sum(r['value'] is None for r in dataset['rows']),
              'actual_simulated_zeros': sum(r['value'] == 0 for r in dataset['rows']),
              'excluded': excluded, 'isolation': checks, 'observed_before_after_identical': True,
              'observed_hashes': before, 'examples': dataset['rows'][:2]}
    write(output / 'generation-manifest.json', result)
    return result


def run(output, *, expected_dataset, expected_code):
    """Frozen train-only fits; tune on validation, then inspect final test once.

    Whole scenario families and related variants are disjoint, in addition to
    chronological embargoes. Held series' own past observations are permitted
    inference context, never training labels or fitted preprocessing input.
    """
    from minder_ml.intelligence.forecasting import (METHODS, RIDGE_ALPHAS, BOOST_DEPTHS,
        FEATURES, fit_candidate, predict, count_metrics)
    if sha(output / 'dataset.json') != expected_dataset or sha(Path(__file__)) != expected_code:
        raise ValueError('immutable_dataset_and_code_hashes_required')
    dataset = json.loads((output / 'dataset.json').read_text())
    prepared, excluded = examples(dataset)
    before = observed_hashes()
    started = time.monotonic()
    fits = 0

    def fit(method, rows, parameter):
        nonlocal fits
        if fits >= 12 or time.monotonic() - started > 120:
            raise RuntimeError('bounded_lab_budget_exhausted')
        model = fit_candidate(method, rows, parameter=parameter)
        fits += 1
        return model

    def peak_mib():
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return peak / (1024*1024 if sys.platform == 'darwin' else 1024)

    pilot = [e for e in prepared if e['entity_type'] == 'role' and e['split'] == 'train'][:16]
    pilot_start = time.monotonic()
    for method in ('ridge', 'gradient_boosting'):
        fit(method, pilot, 2)
    pilot_result = {'fits': 2, 'training_examples': len(pilot),
                    'elapsed_seconds': time.monotonic() - pilot_start,
                    'process_peak_rss_mib': peak_mib(), 'device': 'CPU', 'workers': 1}
    report = {'version': VERSION, 'synthetic': True, 'display_label': LABEL,
              'normal_serving_eligible': False, 'selected_normal_runtime_model': None,
              'real_validation': 'unavailable_no_compatible_real_target_holdout',
              'execution_location': 'local_cpu', 'runpod_job_id': None, 'paid_cost_usd': 0,
              'dataset_sha256': expected_dataset, 'runner_sha256': expected_code,
              'code_base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
              'features': list(FEATURES), 'pilot': pilot_result, 'excluded': excluded,
              'environment': {n: importlib.metadata.version(n) for n in
                              ('numpy', 'scikit-learn', 'scipy', 'xgboost', 'joblib', 'threadpoolctl')},
              'python': sys.version.split()[0], 'family_results': {}, 'artifacts': [],
              'selection_rule': 'Per output family: lowest validation MAE, ties prefer METHODS order; frozen before final test. No normal-runtime promotion.',
              'fit_policy': 'Training families/labels only; no test-time or validation refit. Each method sees the same examples. Parameters chosen only using validation.',
              'split_ids': {s: [e['example_id'] for e in prepared if e['split'] == s]
                            for s in ('train', 'validation', 'test', 'robustness')}}
    frozen, models = {}, {}
    for family in ('role', 'skill'):
        train = [e for e in prepared if e['entity_type'] == family and e['split'] == 'train']
        validation = [e for e in prepared if e['entity_type'] == family and e['split'] == 'validation']
        assert max(e['label_available_at'] for e in train) < min(e['issued_at'] for e in validation)
        held = [e for e in prepared if e['entity_type'] == family and e['split'] in ('test', 'robustness')]
        assert max(e['label_available_at'] for e in validation) < min(e['issued_at'] for e in held)
        trials, configs = {}, {}
        for method in METHODS:
            parameters = RIDGE_ALPHAS if method == 'ridge' else BOOST_DEPTHS if method == 'gradient_boosting' else (None,)
            candidates = []
            for parameter in parameters:
                model = fit(method, train, parameter) if method in ('ridge', 'gradient_boosting') else None
                predictions = predict(method, model, validation)
                metric = count_metrics([e['label'] for e in validation], predictions)
                candidates.append({'parameter': parameter, 'metrics': metric})
                models[(family, method, parameter)] = model
            best = min(candidates, key=lambda t: t['metrics']['mae'])
            configs[method] = best['parameter']
            trials[method] = {'trials': candidates, 'best': best}
        chosen = min(METHODS, key=lambda m: (trials[m]['best']['metrics']['mae'], METHODS.index(m)))
        frozen[family] = {'validation_choice_simulation_only': chosen, 'parameters': configs}
        report['family_results'][family] = {'validation': trials, 'metrics_by_split': {}, 'per_scenario': {}}
    # This artifact exists before *any* final-test predictions or metrics.
    write(output / 'frozen-selection.json', {'synthetic': True, 'normal_serving_eligible': False,
          'selection': frozen, 'dataset_sha256': expected_dataset, 'runner_sha256': expected_code})
    report['frozen_selection_sha256'] = sha(output / 'frozen-selection.json')
    all_predictions = []
    for family in ('role', 'skill'):
        record = report['family_results'][family]
        record.update(frozen[family])
        for method in METHODS:
            parameter = frozen[family]['parameters'][method]
            model = models[(family, method, parameter)]
            for split in ('train', 'validation', 'test', 'robustness'):
                rows = [e for e in prepared if e['entity_type'] == family and e['split'] == split]
                predictions = predict(method, model, rows)
                record['metrics_by_split'].setdefault(split, {})[method] = count_metrics(
                    [e['label'] for e in rows], predictions)
                for scenario in sorted({e['scenario'] for e in rows}):
                    pairs = [(e, p) for e, p in zip(rows, predictions) if e['scenario'] == scenario]
                    record['per_scenario'].setdefault(scenario, {'split': split,
                        'interpretation': 'training_resubstitution_only' if split == 'train' else 'synthetic_' + split,
                        'methods': {}})['methods'][method] = count_metrics(
                            [e['label'] for e, p in pairs], [p for e, p in pairs])
                all_predictions.extend({'synthetic': True, 'display_label': LABEL,
                    'example_id': e['example_id'], 'family': family, 'scenario': e['scenario'],
                    'split': split, 'method': method, 'actual': e['label'], 'prediction': float(p)}
                    for e, p in zip(rows, predictions))
            artifact = output / 'models' / (family + '-' + method + '.joblib')
            artifact.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, artifact)
            metadata = {'synthetic': True, 'display_label': LABEL, 'normal_serving_eligible': False,
                        'dataset_sha256': expected_dataset, 'runner_sha256': expected_code,
                        'label_origin': VERSION + ' fixed fictional equations, not observed ads',
                        'method': method, 'family': family, 'parameter': parameter,
                        'features': list(FEATURES), 'training_example_ids': [e['example_id'] for e in prepared
                            if e['entity_type'] == family and e['split'] == 'train'],
                        'artifact_sha256': sha(artifact), 'artifact': 'models/' + artifact.name,
                        'environment': report['environment']}
            write(artifact.with_suffix('.metadata.json'), metadata)
            report['artifacts'].append(metadata)
    write(output / 'predictions.json', {'synthetic': True, 'display_label': LABEL, 'predictions': all_predictions})
    report['predictions_sha256'] = sha(output / 'predictions.json')
    report['isolation'] = isolation(dataset, output)
    assert before == observed_hashes()
    report.update(fits=fits, elapsed_seconds=time.monotonic() - started,
                  process_peak_rss_mib=peak_mib(), observed_before_after_identical=True,
                  limits={'max_fits': 12, 'max_seconds_between_fit_checks': 120, 'workers': 1},
                  limitations=['Assumed fictional worlds; no independent real demand accuracy',
                               'Training metrics are resubstitution, not holdout evidence',
                               'Validation families differ from training and test; no repeated test-driven tuning',
                               'RSS is process high-water memory including imports; not per-fit allocation',
                               'No calibrated uncertainty, real augmentation benefit or real forecast activation'])
    write(output / 'results.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['generate', 'run'])
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--expected-dataset-sha256')
    parser.add_argument('--expected-code-sha256')
    args = parser.parse_args()
    if args.command == 'generate':
        result = prepare(args.output_dir)
        print(json.dumps({k: v for k, v in result.items() if k not in ('observed_hashes', 'examples')}, indent=2))
    else:
        result = run(args.output_dir, expected_dataset=args.expected_dataset_sha256,
                     expected_code=args.expected_code_sha256)
        print(json.dumps({'synthetic': True, 'fits': result['fits'], 'pilot': result['pilot'],
              'elapsed_seconds': result['elapsed_seconds'], 'process_peak_rss_mib': result['process_peak_rss_mib'],
              'dataset_sha256': result['dataset_sha256'], 'runner_sha256': result['runner_sha256'],
              'measured': {f: {'validation_choice_simulation_only': r['validation_choice_simulation_only'],
                  'test': r['metrics_by_split']['test'], 'robustness': r['metrics_by_split']['robustness']}
                  for f, r in result['family_results'].items()}}, indent=2))


if __name__ == '__main__':
    main()
