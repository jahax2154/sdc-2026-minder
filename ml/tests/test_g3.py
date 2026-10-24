"""G3 conformance tests. Controlled estimator stubs never fit real learners locally."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from minder_ml.intelligence import artifacts, training
from minder_ml.intelligence.data_pipeline import parse_dosm
from minder_ml.intelligence.market_indexes import build_indexes, project_index_rows
from minder_ml.intelligence.inference import recommend
from minder_ml.intelligence.schemas import FeatureSnapshot, RoleInput
from minder_ml.intelligence.policy import ROOT


def observations(template, n=5, equal=False):
    rows=[]
    for year in (2025,2026):
        for i in range(n+1):
            r=copy.deepcopy(template)
            r.update(observation_id='synthetic-test-%s-%s'%(year,i),period_start='%s-04-01'%year,
                period_end='%s-06-30'%year,group_kind='overall' if i==n else 'category',
                value=200 if i==n else 10 if year==2025 else 20 if equal else (i+1)*10,
                data_quality_status='valid',quality_flags=[],occupation_code=None,
                occupation_label='Total' if i==n else 'Synthetic category '+str(i))
            rows.append(r)
    return rows


class MarketIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template=next(r for r in parse_dosm()[0] if r['dimension_scope']=='occupation')

    def current(self, report):
        return next(c for c in report['cohorts'] if c['period_start']=='2026-04-01')

    def test_exact_midrank_formula_and_fixed_projection(self):
        report=build_indexes(observations(self.template))
        cohort=self.current(report)
        self.assertEqual(cohort['cohort_size'],5)
        self.assertEqual(sorted(round(r['market_activity_index'],8) for r in cohort['rows']),[10,30,50,70,90])
        row=cohort['rows'][0]
        selected=project_index_rows(report,[row['observation_id']])[0]
        self.assertEqual(selected['market_activity_index'],row['market_activity_index'])
        self.assertEqual(selected['cohort_hash'],cohort['cohort_hash'])
        self.assertEqual(report,build_indexes(observations(self.template)))

    def test_ties_are_midrank_half(self):
        cohort=self.current(build_indexes(observations(self.template,equal=True)))
        self.assertTrue(all(r['market_activity_index']==50 for r in cohort['rows']))

    def test_minimum_and_missing_history_have_no_reweight(self):
        report=build_indexes(observations(self.template,n=4))
        self.assertEqual(self.current(report)['status'],'no_index_insufficient_eligible_cohort')
        self.assertTrue(all(r['market_activity_index'] is None for r in self.current(report)['rows']))
        rows=observations(self.template);rows[0]['value']=0
        cohort=self.current(build_indexes(rows))
        self.assertEqual(cohort['cohort_size'],4)
        self.assertTrue(any('nonpositive_yoy_denominator' in r['reasons'] for r in cohort['excluded']))

    def test_zero_current_positive_prior_is_real_decline(self):
        rows=observations(self.template);rows[6]['value']=0
        row=next(r for r in self.current(build_indexes(rows))['rows'] if r['observation_id']=='synthetic-test-2026-0')
        self.assertEqual(row['yoy_percent']['value'],-100)
        self.assertEqual(row['share']['value'],0)
        self.assertIsNotNone(row['market_activity_index'])

    def test_quality_and_cohort_separation(self):
        rows=observations(self.template)
        for r in rows:
            if r['period_start']=='2026-04-01':
                r.update(data_quality_status='review_required',quality_flags=['classification_coverage_review'])
        self.assertEqual(self.current(build_indexes(rows))['cohort_size'],0)
        rows=observations(self.template)
        extra=copy.deepcopy(rows)
        for r in extra:
            r['observation_id']='other-source-'+r['observation_id'];r['source_id']='synthetic-other-provider'
        self.assertEqual(len(build_indexes(rows+extra)['cohorts']),4)

    def test_duplicate_revisions_rejected(self):
        rows=observations(self.template);duplicate=copy.deepcopy(rows[0]);duplicate['observation_id']='different-id-same-series'
        with self.assertRaisesRegex(ValueError,'series/window'):build_indexes(rows+[duplicate])


class StubEstimator:
    """Control flow only; not Ridge/XGBoost, career logic or a measured fit."""
    def predict(self,x): return [1.34 for _ in x]
    def get_params(self): return {}


class LearnerGateTests(unittest.TestCase):
    def context(self):return {'preparation_horizon_weeks':12,'role_catalogue_version':'synthetic-test'}
    def roles(self):return [RoleInput('A',FeatureSnapshot(.6,.8,.5,1,.7,1),[])]

    def test_no_runner_blocks_before_construction_or_artifacts(self):
        with patch.object(training,'make_estimator') as construct,patch.object(training,'new_run') as create:
            with self.assertRaisesRegex(ValueError,'runner_unavailable'):
                training.smoke('g3-blocked-test',ROOT/'ml/tests/fixtures/synthetic_math.json',None)
            construct.assert_not_called();create.assert_not_called()

    def test_unavailable_explicit_scorers_keep_contract_and_no_fallback(self):
        for kind in ('ridge','xgboost'):
            r=recommend(self.roles(),profile_version='test',evidence_snapshot_id='test',
                scorer_kind=kind,model_version='missing-g3-artifact',**self.context())
            self.assertEqual(r.result_kind,'model_not_ready');self.assertEqual(r.options,[])
            self.assertEqual(r.unscored_roles[0].personal_fit_index,None)
        r=recommend(self.roles(),profile_version='test',evidence_snapshot_id='test',**self.context())
        self.assertEqual(r.options[0].personal_fit_index,67)
        self.assertIsNone(r.options[0].market_assessment_index)
        self.assertIsNone(r.options[0].overall_match_index)

    def test_experiments_cannot_promote_even_if_status_edited(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(artifacts,'ARTIFACT_ROOT',Path(temp)):
            run=artifacts.run_path('g3-test');run.mkdir()
            meta=artifacts.metadata_base({},self.context(),{}, {})
            meta.update(provenance_mode='policy_distillation',promotable=False,
                evaluation_status='holdout_evaluated',selected_candidate='ridge')
            artifacts.write_json(run/'metadata.json',meta)
            with patch.object(artifacts,'load_pipeline') as load:
                with self.assertRaisesRegex(ValueError,'experimental'):artifacts.load_candidate('g3-test','ridge',self.context())
                load.assert_not_called()

    def test_explicit_experiment_service_and_policy_compatibility(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(artifacts,'ARTIFACT_ROOT',Path(temp)):
            run=artifacts.run_path('g3-test');run.mkdir()
            meta=artifacts.metadata_base({},self.context(),{}, {})
            meta.update(provenance_mode='synthetic_math_only',promotable=False,evaluation_status='synthetic_smoke_only')
            artifacts.write_json(run/'metadata.json',meta)
            with patch.object(artifacts,'load_pipeline',return_value=StubEstimator()):
                r=recommend(self.roles(),profile_version='test',evidence_snapshot_id='test',scorer_kind='ridge',
                    model_version='g3-test',artifact_mode='synthetic_math_only',**self.context())
                self.assertEqual(r.options[0].personal_fit_index,67)
                import jsonschema
                jsonschema.Draft202012Validator(json.loads((ROOT/'contracts/recommendation-result.v1.schema.json').read_text())).validate(r.to_dict())
                self.assertTrue(any('EXPERIMENT ONLY' in w for w in r.warnings))
                meta['policy_sha256']='changed';artifacts.write_json(run/'metadata.json',meta)
                r=recommend(self.roles(),profile_version='test',evidence_snapshot_id='test',scorer_kind='ridge',
                    model_version='g3-test',artifact_mode='synthetic_math_only',**self.context())
                self.assertEqual(r.result_kind,'model_not_ready')

    def test_smoke_control_flow_round_trip_uses_shared_service(self):
        # Sponsor verification, estimator creation and fitting are stubs in this
        # test only. No result is evidence of real RunPod access or learner parity.
        with tempfile.TemporaryDirectory() as temp,patch.object(artifacts,'ARTIFACT_ROOT',Path(temp)), \
             patch.object(artifacts,'require_runpod',return_value={'test_stub_not_runner':True}), \
             patch.object(training,'make_estimator',side_effect=lambda kind:StubEstimator()) as construct, \
             patch.object(artifacts,'fit_timed',return_value={'test_stub_not_fit':True}), \
             patch.object(artifacts,'load_pipeline',side_effect=lambda run,kind,meta:__import__('joblib').load(run/kind/'pipeline.joblib')):
            r=training.smoke('g3-test',ROOT/'ml/tests/fixtures/synthetic_math.json','test-stub')
            self.assertEqual([c.args[0] for c in construct.call_args_list],['ridge','xgboost'])
            self.assertEqual(set(r['report']['candidates']),{'baseline','ridge','xgboost'})
            self.assertFalse(r['promotable'])
            self.assertEqual(r['active_selection'],'baseline')
            meta=json.loads((artifacts.run_path('g3-test')/'metadata.json').read_text())
            self.assertEqual(meta['provenance_mode'],'synthetic_math_only')
            self.assertTrue(all(c['reload_max_absolute_difference']==0 for c in r['candidates'].values()))
            predictions=json.loads((artifacts.run_path('g3-test')/'fixture_predictions.json').read_text())
            self.assertEqual(len(predictions),96)
            self.assertTrue(all(r['report']['candidates'][kind]['shared_service']=='passed' for kind in ('baseline','ridge','xgboost')))
