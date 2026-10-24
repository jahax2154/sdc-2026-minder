"""Local software/mock tests only. None constitutes actual GPU fitting proof."""
from collections import Counter
import base64
import hashlib
import copy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import gpu_control as control
import gpu_synthetic_adapter as adapter
import gpu_worker as worker

ROOT = Path(__file__).resolve().parents[5]


class PreparationTests(unittest.TestCase):
    def safe_budget(self):
        return dict(user_confirmed_credits_and_key=True, balance_verified=True,
            image_pull_verified=True, endpoint_settings_verified=True,
            provider_attempt_bound_verified=True, provider_hard_stop_verified=True,
            artifact_roundtrip_verified=True, automatic_topup=False, billing_upgrade=False,
            max_provider_attempts=1, workers_min=0, workers_max=1, gpu_count=1,
            balance_usd=25, existing_billable_workers=0,
            verified_rate_usd_per_second=.001, verified_total_billable_seconds_bound=365,
            ancillary_and_billing_rounding_usd_bound=.1)

    def test_reuses_immutable_generator_and_splits_without_training(self):
        lab = adapter.load_lab(ROOT)
        data = lab.generate(json.loads(lab.SPEC.read_text()))
        encoded = json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
        self.assertEqual(hashlib.sha256(encoded.encode()).hexdigest(),adapter.DATASET_SHA)
        examples, _ = lab.examples(data)
        self.assertEqual(Counter(e['split'] for e in examples),
                         dict(train=156,validation=24,test=34,robustness=14))

    def test_payload_rejects_changed_dataset_or_cpu_request(self):
        job = {'id':'local-test-only','input':control.PAYLOAD['input']}
        self.assertEqual(worker.validate_payload(job),control.PAYLOAD['input'])
        for change in ({'require_gpu':False},{'dataset_sha256':'wrong'},{'unapproved_feature':True}):
            with self.assertRaises(ValueError):
                worker.validate_payload(dict(job,input=dict(job['input'],**change)))

    def fake_model(self, device='cuda:0', updater='grow_gpu_hist', rounds=48):
        config={'learner':{'generic_param':{'device':device},
            'gradient_booster':{'gbtree_train_param':{'updater':updater}}}}
        booster=SimpleNamespace(save_config=lambda:json.dumps(config),num_boosted_rounds=lambda:rounds)
        return SimpleNamespace(get_booster=lambda:booster)

    def test_GPU_proof_predicate_with_fictional_configs_not_live_proof(self):
        self.assertEqual(adapter.validate_gpu_fit(self.fake_model(),{'USE_CUDA':True})['boosted_rounds'],48)
        for model, info in ((self.fake_model(device='cpu'),{'USE_CUDA':True}),
            (self.fake_model(updater='grow_quantile_histmaker'),{'USE_CUDA':True}),
            (self.fake_model(rounds=0),{'USE_CUDA':True}), (self.fake_model(),{'USE_CUDA':False})):
            with self.assertRaises(RuntimeError): adapter.validate_gpu_fit(model,info)

    def test_no_CUDA_build_fails_before_fitting_or_generation(self):
        import xgboost
        with tempfile.TemporaryDirectory() as directory, patch.object(xgboost,'build_info',return_value={'USE_CUDA':False}):
            with self.assertRaisesRegex(RuntimeError,'no_CPU_fallback'):
                adapter.execute(ROOT,Path(directory),'local-test-not-cloud')

    def test_adapter_metadata_path_with_mocked_fits_is_only_software_evidence(self):
        import xgboost
        from minder_ml.intelligence import forecasting
        reference=json.loads((ROOT/'docs/execution/parallel/B/synthetic-results.v1.json').read_text())
        def write(path,value):
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value)+'\n')
        def simulated_run(output,**kwargs):
            write(output/'frozen-selection.json',{'synthetic':True,'diagnostic':'mock-only'})
            for _ in range(5):
                forecasting.fit_candidate('gradient_boosting',[{'x':[1]*9,'label':1,'example_id':'mock'}],parameter=2)
            result=copy.deepcopy(reference);result['artifacts']=[]
            return result
        lab=SimpleNamespace(prepare=lambda output:{'dataset_sha256':adapter.DATASET_SHA},run=simulated_run,
                            write=write,sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest())
        model=self.fake_model();model.fit=lambda *args:model
        with tempfile.TemporaryDirectory() as directory, \
            patch.object(adapter,'load_lab',return_value=lab), \
            patch.object(xgboost,'build_info',return_value={'USE_CUDA':True}), \
            patch.object(xgboost,'XGBRegressor',return_value=model), \
            patch.object(adapter.subprocess,'check_output',return_value='FICTIONAL-GPU-IN-UNIT-TEST'):
            output=Path(directory)
            result=adapter.execute(ROOT,output,'mock-code-not-cloud')
            selected=json.loads((output/'frozen-selection.json').read_text())['selection']
            self.assertIsInstance(selected,dict)
            self.assertEqual(set(selected),{'role','skill'})
            self.assertTrue(result['previous_selection_preserved'])
            self.assertIn('mixed',result['pilot']['device'])
            self.assertEqual(len(result['gpu_fit_proofs']),5)

    def test_budget_requires_live_evidence_and_USD2_total(self):
        self.assertAlmostEqual(control.budget_check(self.safe_budget()),.465)
        for change in ({'provider_attempt_bound_verified':False},{'max_provider_attempts':2},
            {'workers_max':2},{'balance_usd':1},{'automatic_topup':True},
            {'verified_rate_usd_per_second':1},{'existing_billable_workers':1}):
            with self.assertRaises(ValueError): control.budget_check(dict(self.safe_budget(),**change))

    def test_artifact_roundtrip_before_ephemeral_worker_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=root/'source';source.mkdir()
            (source/'results.json').write_text('{"synthetic":true,"test_only":true}')
            packed=worker.package(source)
            digest=control.retrieve(packed,root/'retrieved')
            self.assertEqual(digest,packed['artifact_sha256'])
            self.assertEqual((root/'retrieved/results.json').read_bytes(),(source/'results.json').read_bytes())
            with self.assertRaises(ValueError): control.retrieve(dict(packed,artifact_sha256='0'*64),root/'bad')

    def test_artifact_path_traversal_rejected(self):
        memory=io.BytesIO()
        with zipfile.ZipFile(memory,'w') as archive: archive.writestr('../escape','bad')
        raw=memory.getvalue()
        packed={'artifact_base64':base64.b64encode(raw).decode(),'artifact_sha256':hashlib.sha256(raw).hexdigest()}
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            control.retrieve(packed,Path(directory))

    def test_failed_child_returns_logs_and_duplicate_cannot_refit(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(worker,'ROOT',Path(directory)), \
            patch.object(worker,'verify_manifest',return_value={'source_commit':'local-test','files':{}}), \
            patch.object(worker.subprocess,'run',return_value=SimpleNamespace(returncode=1)) as run:
            job={'id':'mock-only','input':control.PAYLOAD['input']}
            result=worker.handler(job)
            self.assertEqual(result['status'],'failed'); self.assertFalse(result['gpu_proof'])
            self.assertIn('artifact_base64',result)
            self.assertEqual(worker.handler(job)['status'],'duplicate_rejected')
            self.assertEqual(run.call_count,1)

    def test_success_exit_without_fit_proofs_is_not_GPU_success(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(worker,'ROOT',Path(directory)), \
            patch.object(worker,'verify_manifest',return_value={'source_commit':'local-test','files':{}}), \
            patch.object(worker.subprocess,'run',return_value=SimpleNamespace(returncode=0)):
            result=worker.handler({'id':'mock-only','input':control.PAYLOAD['input']})
            self.assertEqual(result['status'],'failed');self.assertFalse(result['gpu_proof'])

    def test_uncommitted_image_preview_cannot_run_live(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'gpu-image-manifest.json').write_text('{"uncommitted_preparation":true}')
            with self.assertRaisesRegex(ValueError,'uncommitted'): worker.verify_manifest(root)

    def test_management_never_mutates_unrelated_endpoint(self):
        secret={'RUNPOD_ENDPOINT_ID':'test-endpoint','RUNPOD_API_KEY':'fictional-test-key'}
        reply={'data':{'myself':{'endpoints':[{'id':'test-endpoint','name':'unrelated'}]}}}
        with patch.object(control,'api',return_value=reply) as api, self.assertRaisesRegex(ValueError,'non_experiment'):
            control.management('shutdown',secret)
        self.assertEqual(api.call_count,1)  # Only the mocked read query.

    def test_provider_errors_do_not_echo_credential_URL(self):
        secret={'RUNPOD_API_KEY':'fictional-test-key'}
        with patch.object(control,'urlopen',side_effect=OSError('secret-would-be-in-URL')):
            with self.assertRaises(RuntimeError) as caught:
                control.api('POST','https://api.runpod.io/graphql?api_key=fictional-test-key',secret,{})
            self.assertNotIn('fictional-test-key',str(caught.exception))

    def test_ambiguous_submission_cannot_be_retried_even_with_new_receipt_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);image='registry/image@sha256:'+'a'*64
            evidence=dict(self.safe_budget(),verified_endpoint_id='mock-endpoint',verified_image_digest=image)
            preflight=root/'test-only.json';preflight.write_text(json.dumps(evidence))
            secret={'RUNPOD_API_KEY':'fictional-test-key','RUNPOD_ENDPOINT_ID':'mock-endpoint','RUNPOD_IMAGE':image}
            with patch.object(control,'SECRET',root/'.env.runpod.local'), \
                patch.object(control,'load_secret',return_value=secret), \
                patch.object(control,'api',side_effect=RuntimeError('ambiguous-response')) as api:
                with patch('sys.argv',['control','submit','--preflight',str(preflight),'--receipt-dir',str(root/'first')]):
                    with self.assertRaises(RuntimeError): control.main()
                with patch('sys.argv',['control','submit','--preflight',str(preflight),'--receipt-dir',str(root/'second')]):
                    with self.assertRaises(FileExistsError): control.main()
                self.assertEqual(api.call_count,1)
                receipt=(root/'ml/artifacts/session-b/gpu-live/submission-intent.json').read_text()
                self.assertNotIn('fictional-test-key',receipt)


if __name__=='__main__': unittest.main()
