"""Committed market runner: audit sources, then bounded chronological experiments.

No source acquisition, paid launch or training during application inference.
Synthetic fixtures exercise code only and are refused as experiment evidence.
"""
import argparse
from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import time

import joblib

from .data_pipeline import MARKET_DATA, MARKET_ARTIFACTS, encoded, sha, utc_now
from .forecasting import (VERSION, METHODS, RIDGE_ALPHAS, BOOST_DEPTHS, build_examples,
                          temporal_split, rolling_predictions, count_metrics, fit_candidate)
from .market_service import timestamp

PROMOTION_RULE = {
    'version': 'quarter-count-promotion-v1',
    'selection': 'lowest_validation_MAE_then_simpler_method; freeze_before_holdout',
    'minimum_validation_gain_vs_best_baseline': .05,
    'holdout_MAE_must_not_exceed_best_baseline': True,
    'minimum_train_examples': 8, 'minimum_validation_origins': 2, 'minimum_holdout_origins': 2,
    'require_actual_publication_aware_labels': True,
    'require_same_source_universe_and_lead_quarters': True,
    'synthetic_or_revised_vintage_only_backtests_promotable': False,
    'uncertainty': 'validation_absolute_residual_range_not_calibrated',
}


def audit_sources(snapshot):
    rows = snapshot['dosm_observations']
    return {'version': VERSION, 'synthetic': False, 'rows': [],
            'provenance': {'snapshot_version': snapshot['version'],
                           'collected_at': snapshot['collected_at'],
                           'employer_observed_ads': len(snapshot['ads']),
                           'dosm_observation_rows': len(rows),
                           'dosm_quarters': len({r['period_start'] for r in rows}),
                           'dosm_actual_vintage_dates': sorted({r['available_at'] for r in rows})},
            'coverage': {family: {'eligible_quarterly_series': 0, 'reason':
                         'No comparable quarterly unique-ad history; employer active-ad snapshot is not inflow.'}
                         for family in ('role', 'skill')},
            'excluded_source_targets': [
                {'source': 'DOSM JMI', 'rows': len(rows), 'reason':
                 'Broad published offerings are not dedup-verified narrow-role/skill counts; no defensible allocation. '
                 'All cells available in August 2026 vintage; no historical release archive acquired.'},
                {'source': 'Bosch MY', 'rows': len(snapshot['ads']), 'reason':
                 'One incomplete active-ad snapshot, not historical quarterly advertisement inflows.'},
                {'source': 'DOSM labour force/wages', 'reason': 'Different quantities, not advertisement targets.'}],
            'news_comparison': 'unavailable_no_archived_publication_aware_news_features'}


def metrics(predictions):
    return count_metrics([p['actual'] for p in predictions], [p['prediction'] for p in predictions])


def experiment(dataset, *, evaluation_as_of, output_dir, max_fits=80, max_seconds=120):
    if dataset.get('synthetic') is not False:
        raise ValueError('synthetic_or_unspecified_data_cannot_be_real_experiment_evidence')
    prepared = build_examples(dataset['rows'], evaluation_as_of=evaluation_as_of,
                              news_contexts=dataset.get('news_contexts', []))
    if prepared['rejected']:
        raise ValueError('invalid_count_rows:' + json.dumps(prepared['rejected']))
    started = time.monotonic()
    report = {'version': VERSION, 'run_id': 'market-' + evaluation_as_of.replace(':', '-'),
              'evaluation_as_of': evaluation_as_of, 'synthetic': False, 'promotion_rule': PROMOTION_RULE,
              'implementation': {m: 'implemented' for m in METHODS}, 'training': 'not_run',
              'execution_location': 'local_cpu', 'paid_cost_usd': 0, 'fits': 0,
              'actual_series': prepared['series_count'], 'eligible_examples': len(prepared['examples']),
              'news_comparison': 'unavailable_no_archived_features', 'series_results': [],
              'selected_models': [], 'ranking_metrics': None,
              'ranking_reason': 'No cross-series ranking is used; independent count forecasts only.',
              'environment': {k: importlib.metadata.version(k) for k in ('numpy', 'scikit-learn', 'xgboost', 'joblib')}}
    by_series = {}
    for example in prepared['examples']:
        by_series.setdefault(tuple(example['series_key']), []).append(example)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    def run(method, train, held, *, parameter=None, news=False):
        count = len({e['issued_at'] for e in held}) if method not in ('no_change', 'seasonal') else 0
        if report['fits'] + count > max_fits or time.monotonic() - started > max_seconds:
            raise ValueError('bounded_experiment_budget_exhausted')
        result = rolling_predictions(method, train, held, parameter=parameter, news=news)
        report['fits'] += count
        return result
    for key, examples in by_series.items():
        split = temporal_split(examples)
        record = {'series_key': list(key), 'split_status': split['status'], 'reason': split['reason'],
                  'split_ids': {name: [e['example_id'] for e in split[name]] for name in ('train', 'validation', 'holdout')},
                  'validation': {}, 'holdout': {}, 'selected': None}
        report['series_results'].append(record)
        if split['status'] != 'ready':
            continue
        train, validation, holdout = (split[k] for k in ('train', 'validation', 'holdout'))
        # Compare methods on the same temporally held-out examples; tune only on validation.
        configs = {}
        for method in METHODS:
            params = RIDGE_ALPHAS if method == 'ridge' else BOOST_DEPTHS if method == 'gradient_boosting' else (None,)
            trials = []
            for parameter in params:
                try:
                    predictions, folds = run(method, train, validation, parameter=parameter)
                except ValueError as exc:
                    if str(exc).startswith('baseline_not_supported'):
                        continue
                    raise
                trials.append({'parameter': parameter, 'metrics': metrics(predictions),
                               'predictions': predictions, 'folds': folds})
            if trials:
                best = min(trials, key=lambda t: t['metrics']['mae'])
                record['validation'][method] = {'best': best, 'trials': trials}
                configs[method] = best['parameter']
        chosen = min(configs, key=lambda m: (record['validation'][m]['best']['metrics']['mae'], METHODS.index(m)))
        record['frozen_validation_choice'] = chosen
        for method, parameter in configs.items():
            predictions, folds = run(method, train + validation, holdout, parameter=parameter)
            record['holdout'][method] = {'metrics': metrics(predictions), 'predictions': predictions, 'folds': folds}
        # News versus no-news uses identical examples. No zero-fill of missing news.
        matched = [e for e in examples if e['x_news'] is not None]
        matched_split = temporal_split(matched)
        if matched_split['status'] == 'ready':
            report['news_comparison'] = 'matched_validation_only_not_holdout_tuning'
            record['news_ablation'] = {}
            for method in ('ridge', 'gradient_boosting'):
                record['news_ablation'][method] = {}
                for use_news in (False, True):
                    preds, folds = run(method, matched_split['train'], matched_split['validation'],
                                       parameter=configs[method], news=use_news)
                    record['news_ablation'][method]['with_news' if use_news else 'no_news'] = {
                        'metrics': metrics(preds), 'folds': folds}
        baseline_methods = [m for m in ('no_change', 'seasonal') if m in configs]
        baseline_valid = min(record['validation'][m]['best']['metrics']['mae'] for m in baseline_methods)
        baseline_test = min(record['holdout'][m]['metrics']['mae'] for m in baseline_methods)
        valid_error = record['validation'][chosen]['best']['metrics']['mae']
        final_error = record['holdout'][chosen]['metrics']['mae']
        leads = {e['x'][-1] for e in examples}
        promoted = (len(leads) == 1 and final_error <= baseline_test and
                    (chosen in baseline_methods or valid_error <= .95 * baseline_valid))
        record['promotion_status'] = 'selected' if promoted else 'not_selected'
        if promoted:
            eligible = [e for e in examples if timestamp(e['label_available_at']) <= timestamp(evaluation_as_of)]
            if chosen not in baseline_methods:
                if report['fits'] >= max_fits or time.monotonic() - started > max_seconds:
                    raise ValueError('bounded_experiment_budget_exhausted')
            model = None if chosen in baseline_methods else fit_candidate(chosen, eligible, parameter=configs[chosen])
            if model is not None:
                report['fits'] += 1
            artifact = output_dir / (hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16] + '.joblib')
            joblib.dump(model, artifact)
            residuals = [abs(p['prediction'] - p['actual']) for p in record['validation'][chosen]['best']['predictions']]
            selected = {'entity_type': key[0], 'entity_id': key[1], 'series_key': list(key),
                        'method': chosen, 'parameter': configs[chosen], 'lead_quarters': next(iter(leads)),
                        'artifact': artifact.name, 'artifact_sha256': sha(artifact),
                        'model_version': report['run_id'] + ':' + chosen,
                        'uncertainty_radius': max(residuals),
                        'uncertainty_method': PROMOTION_RULE['uncertainty'],
                        'trained_at': evaluation_as_of, 'evaluation_status': 'publication_aware_holdout_passed',
                        'synthetic': False}
            record['selected'] = selected
            report['selected_models'].append(selected)
    report['training'] = 'completed' if report['fits'] else 'not_run'
    report['status'] = 'evaluated' if any(r['holdout'] for r in report['series_results']) else 'unavailable_data'
    report['elapsed_seconds'] = time.monotonic() - started
    report['data_sha256'] = hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest()
    (output_dir / 'results.json').write_text(encoded(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'run'])
    parser.add_argument('--dataset', type=Path)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--code-commit')
    parser.add_argument('--output-dir', type=Path, default=MARKET_ARTIFACTS / 'forecast-run')
    args = parser.parse_args()
    if args.command == 'audit':
        result = audit_sources(json.loads((MARKET_DATA / 'snapshot.v1.json').read_text()))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / 'dataset.json').write_text(encoded(result))
    else:
        if not args.dataset or not args.expected_sha256 or sha(args.dataset) != args.expected_sha256:
            raise ValueError('immutable_dataset_checksum_required')
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        if not args.code_commit or args.code_commit != head:
            raise ValueError('committed_runner_HEAD_must_match_request')
        result = experiment(json.loads(args.dataset.read_text()), evaluation_as_of=utc_now(), output_dir=args.output_dir)
        result.update(code_commit=head, dataset_file_sha256=args.expected_sha256)
        (args.output_dir / 'results.json').write_text(encoded(result))
    print(encoded(result), end='')


if __name__ == '__main__':
    main()
