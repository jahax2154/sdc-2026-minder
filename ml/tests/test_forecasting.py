"""Synthetic software tests only. No real evaluation or promotion evidence."""
import copy
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest

from minder_ml.intelligence.forecasting import (build_examples, temporal_split, feature_vector,
    fit_candidate, predict, count_metrics, rolling_predictions, validate_count_row, history_as_of)
from minder_ml.intelligence.market_training import audit_sources, experiment
from minder_ml.intelligence.data_pipeline import MARKET_DATA


def synthetic_rows(family='role', count=40):
    rows = []
    for i in range(count):
        year, month = 2010 + i // 4, 1 + 3 * (i % 4)
        start = date(year, month, 1)
        following = date(year+1, 1, 1) if month == 10 else date(year, month+3, 1)
        end = following - timedelta(days=1)
        released = (end + timedelta(days=20)).isoformat() + 'T00:00:00Z'
        rows.append({'entity_type': family, 'entity_id': 'synthetic-test-only', 'geography': 'MY',
                     'quantity': 'unique_valid_advertisements', 'unit': 'advertisements',
                     'window_kind': 'quarterly_inflow', 'dedup_verified': True,
                     'source_id': 'synthetic-test', 'source_universe_id': 'synthetic-test-universe',
                     'taxonomy_version': 'test-only', 'method_version': 'test-only',
                     'period': {'start': start.isoformat(), 'end': end.isoformat()},
                     'available_at': released, 'published_at': released,
                     'value': 10 + i*2 + (i % 4)*3})
    return rows


class ForecastTests(unittest.TestCase):
    def examples(self, family='role'):
        return build_examples(synthetic_rows(family), evaluation_as_of='2025-01-01T00:00:00Z')['examples']

    def test_actual_data_audit_never_manufactures_targets(self):
        data = audit_sources(json.loads((MARKET_DATA/'snapshot.v1.json').read_text()))
        self.assertEqual(data['rows'], [])
        self.assertEqual(data['provenance']['dosm_quarters'], 28)
        self.assertEqual(data['provenance']['dosm_actual_vintage_dates'], ['2026-08-18'])
        with tempfile.TemporaryDirectory() as d:
            result = experiment(data, evaluation_as_of='2026-10-23T00:00:00Z', output_dir=d)
            self.assertEqual(result['fits'], 0)
            self.assertEqual(result['status'], 'unavailable_data')
            self.assertEqual(result['selected_models'], [])

    def test_real_runner_refuses_synthetic_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'synthetic'):
                experiment({'synthetic': True, 'rows': synthetic_rows()},
                           evaluation_as_of='2025-01-01T00:00:00Z', output_dir=d)

    def test_families_have_same_time_semantics_with_real_lead(self):
        for family in ('role', 'skill'):
            examples = self.examples(family)
            self.assertGreater(len(examples), 20)
            self.assertTrue(all(e['entity_type'] == family for e in examples))
            self.assertTrue(all(e['x'][-1] == 2 for e in examples))
            self.assertTrue(all(e['lead_days_to_target_start'] > 60 for e in examples))
            self.assertTrue(all(e['x_news'] is None for e in examples))

    def test_delayed_vintage_has_no_historical_backtest(self):
        rows = synthetic_rows()
        for row in rows:
            row['published_at'] = row['available_at'] = '2026-08-18T00:00:00Z'
        result = build_examples(rows, evaluation_as_of='2026-10-23T00:00:00Z')
        self.assertEqual(result['examples'], [])

    def test_missing_quarter_and_invalid_target(self):
        rows = synthetic_rows()
        with self.assertRaisesRegex(ValueError, 'history_gap'):
            feature_vector(rows[:2] + rows[3:5], {'start': '2012-01-01', 'end': '2012-03-31'})
        row = copy.deepcopy(rows[0]);row['window_kind'] = 'active_snapshot'
        with self.assertRaisesRegex(ValueError, 'incompatible_count'):
            validate_count_row(row)
        row = copy.deepcopy(rows[0]);row['period']['end'] = '2010-04-01'
        with self.assertRaisesRegex(ValueError, 'incorrect_quarter'):
            validate_count_row(row)

    def test_revisions_obey_actual_availability(self):
        rows = synthetic_rows()[:5]
        revision = dict(rows[0], value=999, available_at='2024-01-01T00:00:00Z')
        self.assertEqual(history_as_of(rows+[revision], '2015-01-01T00:00:00Z')[0]['value'], rows[0]['value'])
        self.assertEqual(history_as_of(rows+[revision], '2025-01-01T00:00:00Z')[0]['value'], 999)

    def test_temporal_embargo_training_transform_and_rolling_folds(self):
        split = temporal_split(self.examples())
        self.assertEqual(split['status'], 'ready')
        valid_start = min(e['issued_at'] for e in split['validation'])
        self.assertTrue(all(e['label_available_at'] <= valid_start for e in split['train']))
        ids = [{e['example_id'] for e in split[k]} for k in ('train', 'validation', 'holdout')]
        self.assertFalse(ids[0] & ids[1] or ids[1] & ids[2] or ids[0] & ids[2])
        model = fit_candidate('ridge', split['train'], parameter=10)
        expected = sum(e['x'][0] for e in split['train']) / len(split['train'])
        self.assertAlmostEqual(model[0].mean_[0], expected)
        for method in ('no_change', 'seasonal', 'ridge', 'gradient_boosting'):
            preds, folds = rolling_predictions(method, split['train'], split['validation'], parameter=2)
            self.assertEqual(len(preds), len(split['validation']))
            self.assertTrue(all(p['prediction'] >= 0 for p in preds))
            for fold in folds:
                self.assertFalse(set(fold['train_ids']) & set(fold['test_ids']))

    def test_zeros_and_news_availability(self):
        self.assertIsNone(count_metrics([0, 0], [0, 1])['wape'])
        self.assertEqual(count_metrics([0, 0], [0, 1])['zero_targets'], 2)
        context = {'entity_type': 'role', 'entity_id': 'synthetic-test-only',
                   'source_universe_id': 'synthetic-test-universe', 'complete_coverage': True,
                   'window_end': '2010-12-31', 'available_at': '2099-01-01T00:00:00Z',
                   'attention_rate': .2}
        result = build_examples(synthetic_rows(), evaluation_as_of='2025-01-01T00:00:00Z', news_contexts=[context])
        self.assertTrue(all(e['x_news'] is None for e in result['examples']))


if __name__ == '__main__':
    unittest.main()
