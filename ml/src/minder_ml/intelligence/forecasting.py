"""Publication-aware direct next-calendar-quarter advertisement forecasting.

Internal records preserve their declared source population, quarter flow, unit,
taxonomy/method version and actual availability. Snapshot stocks, source scores,
foreign data and unverified broad-to-narrow allocations cannot enter this task.
"""
from collections import defaultdict
from datetime import datetime, date
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from threadpoolctl import threadpool_limits

from .market_service import timestamp
from .service_contracts import next_calendar_quarter

VERSION = 'my-quarterly-unique-ads-v1'
METHODS = ('no_change', 'seasonal', 'ridge', 'gradient_boosting')
RIDGE_ALPHAS = (1., 10., 100.)
BOOST_DEPTHS = (2, 3)
FEATURES = ('latest_count', 'lag1', 'lag2', 'lag3', 'mean4', 'recent_change',
            'target_quarter_sin', 'target_quarter_cos', 'lead_quarters')


def quarter_number(day):
    d = date.fromisoformat(day[:10])
    return d.year * 4 + (d.month - 1) // 3


def feature_vector(history, target_period):
    history = sorted(history, key=lambda r: r['period']['start'])
    if len(history) < 4:
        raise ValueError('at_least_four_contiguous_quarters_required')
    last = history[-4:]
    q = [quarter_number(r['period']['start']) for r in last]
    if q != list(range(q[-1] - 3, q[-1] + 1)):
        raise ValueError('history_gap_no_imputation')
    values = [r['value'] for r in last]
    if any(v is None or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('missing_or_invalid_counts')
    target_q = quarter_number(target_period['start'])
    lead = target_q - q[-1]
    if lead < 1:
        raise ValueError('forecast_target_must_follow_last_observation')
    return [values[-1], values[-2], values[-3], values[-4], float(np.mean(values)),
            values[-1] - values[-2], math.sin(2 * math.pi * (target_q % 4) / 4),
            math.cos(2 * math.pi * (target_q % 4) / 4), lead]


def validate_count_row(row):
    if row['entity_type'] not in ('role', 'skill') or row['geography'] != 'MY':
        raise ValueError('requires_Malaysian_role_or_skill')
    if (row['quantity'] != 'unique_valid_advertisements' or row['unit'] != 'advertisements'
            or row['window_kind'] != 'quarterly_inflow' or not row['dedup_verified']):
        raise ValueError('incompatible_count_target_or_unverified_deduplication')
    start, end = row['period']['start'], row['period']['end']
    # Shared helper supplies the exact quarter bounds, including leap years.
    year, month = int(start[:4]), int(start[5:7])
    if month not in (1, 4, 7, 10) or start[8:] != '01':
        raise ValueError('not_a_full_calendar_quarter')
    prev = f'{year - 1}-12-01T00:00:00Z' if month == 1 else f'{year}-{month-1:02d}-01T00:00:00Z'
    if next_calendar_quarter(prev) != row['period']:
        raise ValueError('incorrect_quarter_end')
    if not row['source_id'] or not row['source_universe_id'] or not row['taxonomy_version'] or not row['method_version']:
        raise ValueError('missing_source_comparability_identity')
    published, available = timestamp(row['published_at']), timestamp(row['available_at'])
    if available < published or available.date() < date.fromisoformat(end):
        raise ValueError('availability_precedes_publication_or_observation')
    value = row['value']
    if value is not None and (not math.isfinite(value) or value < 0 or int(value) != value):
        raise ValueError('invalid_advertisement_count')


def series_key(row):
    return tuple(row[k] for k in ('entity_type', 'entity_id', 'geography', 'source_universe_id',
                                 'quantity', 'unit', 'taxonomy_version', 'method_version'))


def history_as_of(rows, issue):
    latest = {}
    for row in sorted(rows, key=lambda r: timestamp(r['available_at'])):
        if timestamp(row['available_at']) <= timestamp(issue) and row['period']['end'] < issue[:10]:
            latest[row['period']['start']] = row
    return [latest[k] for k in sorted(latest)]


def build_examples(rows, *, evaluation_as_of, news_contexts=()):
    """Labels may arrive after issue; training folds enforce label availability.

    Issue origins are *actual* releases, not invented historical release dates.
    Quarter target is derived from issue date, with variable lead since last row.
    """
    groups, rejected, examples = defaultdict(list), [], []
    identities = set()
    for index, row in enumerate(rows):
        try:
            validate_count_row(row)
            key = series_key(row)
            identity = (key, row['period']['start'], row['available_at'])
            if identity in identities:
                raise ValueError('duplicate_series_period_vintage')
            identities.add(identity)
            groups[key].append(row)
        except (KeyError, ValueError, TypeError) as exc:
            rejected.append({'row': index, 'reason': str(exc)})
    for key, group in groups.items():
        truth = {r['period']['start']: r for r in history_as_of(group, evaluation_as_of)}
        for issue in sorted({r['available_at'] for r in group if timestamp(r['available_at']) <= timestamp(evaluation_as_of)}):
            target = next_calendar_quarter(issue)
            label = truth.get(target['start'])
            if label is None or label['value'] is None:
                continue
            history = history_as_of(group, issue)
            try:
                x = feature_vector(history, target)
            except ValueError:
                continue
            contexts = [c for c in news_contexts if c['entity_type'] == key[0] and c['entity_id'] == key[1]
                        and c['source_universe_id'] == key[3] and c['complete_coverage']
                        and c['window_end'] < issue[:10] and timestamp(c['available_at']) <= timestamp(issue)]
            context = max(contexts, key=lambda c: timestamp(c['available_at']), default=None)
            x_news = x + [context['attention_rate']] if context and math.isfinite(context['attention_rate']) else None
            seasonal = next((r['value'] for r in history
                             if quarter_number(r['period']['start']) == quarter_number(target['start']) - 4), None)
            example = {'series_key': list(key), 'entity_type': key[0], 'entity_id': key[1],
                       'issued_at': issue, 'target_period': target, 'label': label['value'],
                       'label_available_at': label['available_at'], 'x': x, 'x_news': x_news,
                       'latest_period': history[-1]['period'], 'no_change': history[-1]['value'],
                       'seasonal': seasonal, 'source_ids': sorted({r['source_id'] for r in history}),
                       'last_available_at': history[-1]['available_at'],
                       'lead_days_to_target_start': (date.fromisoformat(target['start']) - timestamp(issue).date()).days,
                       'days_since_last_observation_to_target_start': (date.fromisoformat(target['start']) -
                           date.fromisoformat(history[-1]['period']['end'])).days}
            example['example_id'] = hashlib.sha256(json.dumps([key, issue, target], sort_keys=True).encode()).hexdigest()
            examples.append(example)
    examples.sort(key=lambda e: (timestamp(e['issued_at']), e['entity_type'], e['entity_id']))
    return {'examples': examples, 'rejected': rejected, 'series_count': len(groups),
            'version': VERSION, 'evaluation_as_of': evaluation_as_of}


def temporal_split(examples, *, holdout_origins=2, validation_origins=2):
    origins = sorted({e['issued_at'] for e in examples}, key=timestamp)
    if len(origins) < holdout_origins + validation_origins + 8:
        return {'status': 'unavailable', 'reason': 'insufficient_distinct_temporal_origins',
                'train': [], 'validation': [], 'holdout': []}
    holdout_start = origins[-holdout_origins]
    # Publication delay can leave an embargo between validation and holdout.
    valid_candidates = sorted({e['issued_at'] for e in examples
                               if timestamp(e['issued_at']) < timestamp(holdout_start)
                               and timestamp(e['label_available_at']) <= timestamp(holdout_start)}, key=timestamp)
    if len(valid_candidates) < validation_origins:
        return {'status': 'unavailable', 'reason': 'insufficient_published_validation_labels',
                'train': [], 'validation': [], 'holdout': []}
    valid_issues = set(valid_candidates[-validation_origins:])
    valid_start = min(valid_issues, key=timestamp)
    # Only outcomes genuinely known at each boundary may train/tune a model.
    train = [e for e in examples if timestamp(e['issued_at']) < timestamp(valid_start)
             and timestamp(e['label_available_at']) <= timestamp(valid_start)]
    validation = [e for e in examples if e['issued_at'] in valid_issues
                  and timestamp(e['label_available_at']) <= timestamp(holdout_start)]
    holdout = [e for e in examples if timestamp(e['issued_at']) >= timestamp(holdout_start)]
    status = 'ready' if len(train) >= 8 and len(validation) >= 2 and len(holdout) >= 2 else 'unavailable'
    return {'status': status, 'reason': None if status == 'ready' else 'insufficient_publication_aware_split',
            'train': train, 'validation': validation, 'holdout': holdout}


def fit_candidate(method, examples, *, parameter=None, news=False):
    """Preprocessors fit on this explicit training subset only. CPU bounded."""
    if method not in ('ridge', 'gradient_boosting'):
        raise ValueError('only_learned_candidates_are_fitted')
    key = 'x_news' if news else 'x'
    if not examples or any(e[key] is None for e in examples):
        raise ValueError('missing_training_features')
    x, y = np.asarray([e[key] for e in examples]), np.asarray([e['label'] for e in examples])
    if method == 'ridge':
        # Explicit SVD avoids platform BLAS floating-point warnings in the auto
        # Cholesky solver on this small collinear lag feature matrix.
        model = make_pipeline(StandardScaler(), Ridge(alpha=10. if parameter is None else parameter, solver='svd'))
    else:
        model = XGBRegressor(n_estimators=48, max_depth=2 if parameter is None else parameter,
                             learning_rate=.05, objective='reg:squarederror', random_state=23,
                             n_jobs=1, tree_method='hist', subsample=1., colsample_bytree=1.)
    with threadpool_limits(limits=1):
        return model.fit(x, y)


def predict(method, model, examples, *, news=False):
    if method in ('no_change', 'seasonal'):
        values = [e[method] for e in examples]
        if any(v is None for v in values):
            raise ValueError('baseline_not_supported_for_all_examples')
        return np.asarray(values, dtype=float)
    with threadpool_limits(limits=1):
        values = model.predict(np.asarray([e['x_news' if news else 'x'] for e in examples]))
    if not np.isfinite(values).all():
        raise ValueError('non_finite_model_predictions')
    return np.maximum(0., values)


def count_metrics(actual, predicted):
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    if not len(actual) or not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError('finite_nonempty_evaluation_required')
    error = predicted - actual
    denominator = float(np.abs(actual).sum())
    return {'mae': float(np.abs(error).mean()), 'rmse': float(np.sqrt(np.mean(error ** 2))),
            'wape': float(np.abs(error).sum() / denominator) if denominator else None,
            'zero_targets': int((actual == 0).sum()), 'n': len(actual)}


def rolling_predictions(method, train, held_out, *, parameter=None, news=False):
    """Expanding refits at each held-out issue, never using future outcomes."""
    predictions, fits = [], []
    pool = list(train)
    for issue in sorted({e['issued_at'] for e in held_out}, key=timestamp):
        batch = [e for e in held_out if e['issued_at'] == issue]
        eligible = [e for e in pool if timestamp(e['issued_at']) < timestamp(issue)
                    and timestamp(e['label_available_at']) <= timestamp(issue)]
        if len(eligible) < 8:
            raise ValueError('insufficient_as_of_training_examples')
        model = None if method in ('no_change', 'seasonal') else fit_candidate(method, eligible, parameter=parameter, news=news)
        values = predict(method, model, batch, news=news)
        predictions.extend(dict(example_id=e['example_id'], issued_at=issue, actual=e['label'],
                                prediction=float(v), entity_id=e['entity_id']) for e, v in zip(batch, values))
        fits.append({'issued_at': issue, 'train_ids': [e['example_id'] for e in eligible],
                     'test_ids': [e['example_id'] for e in batch]})
        pool.extend(batch)
    return predictions, fits


def serve_forecast(registry, entity_type, entity_id, issued_at):
    """B3 loads only independently checked selected registry entries."""
    return registry.forecast(entity_type, entity_id, issued_at=issued_at)


class ForecastRegistry:
    """Load explicitly selected, trusted lane artifacts after compatibility gates.

    Joblib is a trusted-operator format, never an upload accepted from end users.
    The checksummed registry/dataset must come from reviewed release contents.
    No models are selected in the delivered empty-data registry.
    """
    def __init__(self, path=None, *, artifact_root=None):
        import importlib.metadata
        from .data_pipeline import MARKET_DATA, MARKET_ARTIFACTS, sha
        self.path = Path(path) if path is not None else MARKET_DATA / 'serving-registry.v1.json'
        self.manifest = json.loads(self.path.read_text())
        m = self.manifest
        if (m.get('version') != 'market-serving-registry-v1' or m.get('forecast_spec') != VERSION
                or m.get('synthetic') is not False or m.get('features') != list(FEATURES)
                or m.get('promotion_rule_version') != 'quarter-count-promotion-v1'):
            raise ValueError('incompatible_or_synthetic_forecast_registry')
        self.artifact_root = Path(artifact_root or MARKET_ARTIFACTS / 'forecast-run').resolve()
        dataset_path = (self.path.parent / m['dataset']['file']).resolve()
        if not dataset_path.is_relative_to(self.path.parent.resolve()) or sha(dataset_path) != m['dataset']['sha256']:
            raise ValueError('forecast_dataset_checksum_or_path_mismatch')
        self.dataset = json.loads(dataset_path.read_text())
        if self.dataset.get('synthetic') is not False:
            raise ValueError('synthetic_dataset_not_served')
        for row in self.dataset['rows']:
            validate_count_row(row)
        if len({(series_key(r), r['period']['start'], r['available_at']) for r in self.dataset['rows']}) != len(self.dataset['rows']):
            raise ValueError('duplicate_forecast_dataset_rows')
        identities = set()
        for entry in m['models']:
            identity = (entry['entity_type'], entry['entity_id'])
            if identity in identities:
                raise ValueError('multiple_selected_models_for_same_entity')
            identities.add(identity)
            if (entry.get('synthetic') is not False
                    or entry.get('evaluation_status') != 'publication_aware_holdout_passed'
                    or entry.get('method') not in METHODS
                    or not isinstance(entry.get('lead_quarters'), int) or entry['lead_quarters'] < 1
                    or entry.get('uncertainty_method') != 'validation_absolute_residual_range_not_calibrated'
                    or not math.isfinite(entry['uncertainty_radius']) or entry['uncertainty_radius'] < 0):
                raise ValueError('non_promotable_model')
            if entry['series_key'][:2] != list(identity):
                raise ValueError('model_entity_identity_mismatch')
            if not any(list(series_key(r)) == entry['series_key'] for r in self.dataset['rows']):
                raise ValueError('selected_model_has_no_compatible_observations')
            if set(m['environment']) != {'numpy', 'scikit-learn', 'xgboost', 'joblib'}:
                raise ValueError('forecast_environment_manifest_incomplete')
            for package, version in m['environment'].items():
                if importlib.metadata.version(package) != version:
                    raise ValueError('forecast_environment_version_mismatch')
            self._artifact_path(entry)  # Verify every checksum before deserializing any model.
        self.loaded = {}

    def _artifact_path(self, entry):
        from .data_pipeline import sha
        artifact = (self.artifact_root / entry['artifact']).resolve()
        if not artifact.is_relative_to(self.artifact_root) or sha(artifact) != entry['artifact_sha256']:
            raise ValueError('forecast_artifact_checksum_or_path_mismatch')
        return artifact

    def forecast(self, entity_type, entity_id, *, issued_at):
        entry = next((e for e in self.manifest['models']
                      if e['entity_type'] == entity_type and e['entity_id'] == entity_id), None)
        if entry is None:
            return None
        def unavailable(reason):
            return {'status': 'unavailable', 'value': None, 'internal_index': None,
                    'uncertainty': {'lower': None, 'upper': None, 'method': None},
                    'missing_reasons': [reason],
                    'explanation': 'Next-quarter forecast unavailable: ' + reason.replace('_', ' ') + '.'}
        if timestamp(entry['trained_at']) > timestamp(issued_at):
            return unavailable('selected_model_not_available_at_issue')
        if timestamp(self.manifest['created_at']) > timestamp(issued_at):
            return unavailable('forecast_registry_not_available_at_issue')
        rows = [r for r in self.dataset['rows'] if list(series_key(r)) == entry['series_key']]
        history = history_as_of(rows, issued_at)
        target = next_calendar_quarter(issued_at)
        try:
            x = feature_vector(history, target)
        except ValueError as exc:
            return unavailable(str(exc))
        if x[-1] != entry['lead_quarters']:
            return unavailable('selected_model_not_evaluated_for_actual_lead_quarters')
        if not history:
            return unavailable('no_observations_available_at_issue')
        seasonal = next((r['value'] for r in history
                         if quarter_number(r['period']['start']) == quarter_number(target['start']) - 4), None)
        example = {'x': x, 'no_change': history[-1]['value'], 'seasonal': seasonal}
        identity = (entity_type, entity_id)
        if identity not in self.loaded:
            import joblib
            self.loaded[identity] = joblib.load(self._artifact_path(entry))
        try:
            value = float(predict(entry['method'], self.loaded[identity], [example])[0])
        except ValueError as exc:
            return unavailable(str(exc))
        radius = entry['uncertainty_radius']
        return {'status': 'available', 'value': value, 'internal_index': None,
                'source_universe_id': entry['series_key'][3],
                'cohort_version': self.manifest['dataset']['sha256'],
                'measurement': 'forecast_unique_valid_advertisements_in_target_quarter',
                'unit': 'advertisements', 'denominator': 'declared source universe; not all Malaysian jobs',
                'observation_period': history[-1]['period'],
                'published_at': entry['trained_at'], 'available_at': entry['trained_at'],
                'ingested_at': self.manifest['created_at'],
                'source_ids': sorted({r['source_id'] for r in history}),
                'model_version': entry['model_version'], 'missing_reasons': [],
                'uncertainty': {'lower': max(0., value - radius), 'upper': value + radius,
                                'method': entry['uncertainty_method']},
                'explanation': f'Estimated advertisements in {target["start"]} to {target["end"]} '
                    f'within the declared source universe. Last observed quarter ended {history[-1]["period"]["end"]}; '
                    f'lead {int(x[-1])} quarters from that observation. Validation residual range is descriptive, '
                    'not a calibrated confidence interval or hiring guarantee.'}
