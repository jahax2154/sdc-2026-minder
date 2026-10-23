"""Isolated fictional count scenarios. Never an observed-data or serving runner."""
import argparse
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import random

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


def observed_hashes():
    # Includes the unchanged normal registry, original inputs and all market data
    # except the explicitly isolated lab specification namespace.
    paths = [p for p in MARKET_DATA.rglob('*') if p.is_file() and 'synthetic-lab' not in p.parts]
    manifest = json.loads(Path('docs/execution/parallel/source_snapshot.v1.json').read_text())
    paths += [Path('ml/minder_ml_starter') / r['path'] for r in manifest['source_files']]
    return {str(p): sha(p) for p in sorted(paths)}


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['generate'])
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = prepare(args.output_dir)
    print(json.dumps({k: v for k, v in result.items() if k not in ('observed_hashes', 'examples')}, indent=2))


if __name__ == '__main__':
    main()
