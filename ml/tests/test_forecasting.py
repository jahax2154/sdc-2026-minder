"""Synthetic software tests only. No real evaluation or promotion evidence."""
import copy
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import importlib.metadata
import joblib

from minder_ml.intelligence.forecasting import (build_examples, temporal_split, feature_vector,
    fit_candidate, predict, count_metrics, rolling_predictions, validate_count_row, history_as_of)
from minder_ml.intelligence.forecasting import ForecastRegistry, VERSION, FEATURES, series_key
from minder_ml.intelligence.market_training import audit_sources, experiment
from minder_ml.intelligence.data_pipeline import MARKET_DATA, sha, encoded


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
        source_audits={r['source']:r for r in data['excluded_source_targets']}
        self.assertEqual(source_audits['DOSM explicit published role facts']['observations'],35)
        self.assertEqual(source_audits['DOSM explicit published role facts']['max_numeric_points_per_series'],7)
        self.assertEqual(source_audits['JobStreet original frozen corpus']['unique_job_ids'],69024)
        self.assertFalse(source_audits['JobStreet original frozen corpus']['collection_windows_known'])
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

    def test_news_feature_boundary_excludes_personal_posts_and_missing_coverage(self):
        context = {'entity_type': 'role', 'entity_id': 'synthetic-test-only',
                   'source_universe_id': 'synthetic-test-universe', 'complete_coverage': True,
                   'pipeline_version': 'credible-events-v1', 'source_ids': ['mida-official'],
                   'underlying_document_sha256': ['a'*64], 'window_start': '2010-01-01',
                   'window_end': '2010-12-31', 'available_at': '2011-01-01T00:00:00Z',
                   'attention_rate': .2, 'coverage': [{'source_id': 'mida-official', 'documents': 5,
                     'complete': True, 'start': '2010-01-01', 'end': '2010-12-31',
                     'available_at': '2011-01-01T00:00:00Z'}]}
        def result(c):
            return build_examples(synthetic_rows(),evaluation_as_of='2025-01-01T00:00:00Z',news_contexts=[c])['examples']
        self.assertTrue(any(e['x_news'] is not None for e in result(context)))
        anonymous = dict(context,source_ids=['personal-post'])
        no_coverage = dict(context,coverage=[])
        for bad in (anonymous, no_coverage, dict(context, underlying_document_sha256=[])):
            self.assertTrue(all(e['x_news'] is None for e in result(bad)))


class RegistryTests(unittest.TestCase):
    """Temporary fake acceptance metadata exercises loader branches only.

    These are fictional software fixtures, never a real promotion/evaluation.
    No fixture artifact or predictions are exported as application evidence.
    """
    def fixture(self, folder):
        rows = synthetic_rows()
        dataset = folder/'dataset.json'
        dataset.write_text(encoded({'synthetic': False, 'fixture_only': True, 'rows': rows}))
        artifact = folder/'baseline.joblib'
        joblib.dump(None, artifact)
        entry = {'entity_type': 'role', 'entity_id': 'synthetic-test-only',
                 'series_key': list(series_key(rows[0])), 'method': 'no_change', 'lead_quarters': 2,
                 'artifact': artifact.name, 'artifact_sha256': sha(artifact),
                 'synthetic': False, 'evaluation_status': 'publication_aware_holdout_passed',
                 'trained_at': '2020-01-20T00:00:00Z', 'model_version': 'test-only',
                 'uncertainty_radius': 5., 'uncertainty_method': 'validation_absolute_residual_range_not_calibrated'}
        manifest = {'version': 'market-serving-registry-v1', 'forecast_spec': VERSION,
                    'synthetic': False, 'features': list(FEATURES), 'promotion_rule_version': 'quarter-count-promotion-v1',
                    'created_at': '2020-01-20T00:00:00Z', 'dataset': {'file': dataset.name, 'sha256': sha(dataset)},
                    'models': [entry], 'environment': {k: importlib.metadata.version(k)
                                                      for k in ('numpy','scikit-learn','xgboost','joblib')}}
        registry = folder/'registry.json';registry.write_text(encoded(manifest))
        return registry, manifest, artifact

    def test_packaged_registry_has_no_selected_models(self):
        registry = ForecastRegistry()
        self.assertEqual(registry.manifest['models'], [])
        self.assertIsNone(registry.forecast('skill','source-term:sql',issued_at='2026-10-23T00:00:00Z'))
        self.assertEqual(registry.loaded, {})

    def test_load_trusted_fixture_baseline_and_reject_wrong_lead(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);path,manifest,artifact=self.fixture(folder)
            registry=ForecastRegistry(path,artifact_root=folder)
            self.assertEqual(registry.loaded,{})
            result=registry.forecast('role','synthetic-test-only',issued_at='2020-01-21T00:00:00Z')
            self.assertEqual(result['value'],synthetic_rows()[-1]['value'])
            self.assertEqual(result['observation_period']['end'],'2019-12-31')
            self.assertEqual(result['uncertainty']['upper']-result['value'],5)
            wrong=registry.forecast('role','synthetic-test-only',issued_at='2020-07-01T00:00:00Z')
            self.assertIsNone(wrong['value'])
            self.assertIn('actual_lead_quarters',wrong['missing_reasons'][0])
            prior=registry.forecast('role','synthetic-test-only',issued_at='2019-01-01T00:00:00Z')
            self.assertIsNone(prior['value'])

    def test_compatibility_and_hashes_reject_before_deserializing(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);path,manifest,artifact=self.fixture(folder)
            with patch('joblib.load') as load:
                artifact.write_bytes(b'corrupted')
                with self.assertRaisesRegex(ValueError,'checksum'):
                    ForecastRegistry(path,artifact_root=folder)
                manifest['models'][0]['artifact_sha256']=sha(artifact)
                manifest['models'][0]['synthetic']=True;path.write_text(encoded(manifest))
                with self.assertRaisesRegex(ValueError,'non_promotable'):
                    ForecastRegistry(path,artifact_root=folder)
                manifest['models'][0]['synthetic']=False
                manifest['environment']['scikit-learn']='incompatible-test-version';path.write_text(encoded(manifest))
                with self.assertRaisesRegex(ValueError,'environment'):
                    ForecastRegistry(path,artifact_root=folder)
                load.assert_not_called()

    def test_dataset_and_artifact_path_containment(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);path,manifest,artifact=self.fixture(folder)
            manifest['dataset']['file']='../escape.json';path.write_text(encoded(manifest))
            with self.assertRaisesRegex(ValueError,'path_mismatch'):
                ForecastRegistry(path,artifact_root=folder)
            path,manifest,artifact=self.fixture(folder)
            manifest['models'][0]['artifact']='../escape.joblib';path.write_text(encoded(manifest))
            with self.assertRaisesRegex(ValueError,'path_mismatch'):
                ForecastRegistry(path,artifact_root=folder)


if __name__ == '__main__':
    unittest.main()
