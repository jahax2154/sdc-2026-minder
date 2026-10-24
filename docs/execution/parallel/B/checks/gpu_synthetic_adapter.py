"""GPU execution adapter for the unchanged, hash-pinned synthetic experiment.

Does not import RunPod or provision resources. CPU fallback is a failed GPU fit.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace

PINNED_RUNNER_SHA = 'd20ea421410e453cee1a444dc530e86ef3d94f2caf3635b2b6e3a87ade6a5b0b'
DATASET_SHA = 'b7aa327d30220b27a2236476b5c51d45d04deb16d9bfb009cc2fcca81a01880b'


def validate_gpu_fit(model, build_info):
    config = json.loads(model.get_booster().save_config())
    learner = config['learner']
    device = learner['generic_param']['device']
    updater = learner['gradient_booster'].get('gbtree_train_param', {}).get('updater', '')
    rounds = model.get_booster().num_boosted_rounds()
    if not build_info.get('USE_CUDA') or not device.startswith('cuda') or 'gpu' not in updater or rounds != 48:
        raise RuntimeError('GPU_fit_not_proven_or_CPU_fallback')
    return {'effective_device': device, 'updater': updater, 'boosted_rounds': rounds,
            'fitted_config': config, 'config_sha256': hashlib.sha256(
                model.get_booster().save_config().encode()).hexdigest()}


def load_lab(root):
    pinned = json.loads((root / 'docs/execution/parallel/B/synthetic-runpod-job.v1.json').read_text())
    for name, expected in pinned['immutable_inputs'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('original_CPU_launch_contract_changed:' + name)
    path = root / 'docs/execution/parallel/B/checks/synthetic_market_experiment.py'
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINNED_RUNNER_SHA:
        raise ValueError('original_runner_checksum_mismatch')
    spec = importlib.util.spec_from_file_location('pinned_synthetic_lab', path)
    lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
    return lab


def execute(root, output, source_commit):
    import numpy as np
    import xgboost as xgb
    from threadpoolctl import threadpool_limits
    from minder_ml.intelligence import forecasting
    root, output = Path(root), Path(output)
    os.chdir(root)
    lab = load_lab(root)
    build_info = xgb.build_info()
    if not build_info.get('USE_CUDA'):
        raise RuntimeError('CUDA_enabled_XGBoost_build_required; no_CPU_fallback')
    gpu_inventory = subprocess.check_output(['nvidia-smi', '--query-gpu=name,uuid,driver_version,memory.total',
                                             '--format=csv,noheader'], text=True).strip()
    generation = lab.prepare(output)
    if generation['dataset_sha256'] != DATASET_SHA:
        raise ValueError('declared_dataset_changed')
    reference = json.loads((root / 'docs/execution/parallel/B/synthetic-results.v1.json').read_text())
    previous_selection = {family: {'validation_choice_simulation_only': record['validation_choice_simulation_only'],
                        'parameters': record['parameters']}
                for family, record in reference['family_results'].items()}
    lab.write(output / 'previous-frozen-selection.json', {'synthetic': True, 'selection': previous_selection,
              'authority': 'SY2 prior validation; recorded before GPU fitting or test predictions'})
    original_fit, original_predict = forecasting.fit_candidate, forecasting.predict
    fit_proofs = []

    def fit(method, examples, *, parameter=None, news=False):
        if method != 'gradient_boosting':
            return original_fit(method, examples, parameter=parameter, news=news)
        if news:
            raise ValueError('undeclared_news_experiment')
        model = xgb.XGBRegressor(n_estimators=48, max_depth=2 if parameter is None else parameter,
            learning_rate=.05, objective='reg:squarederror', random_state=23, n_jobs=1,
            tree_method='hist', subsample=1., colsample_bytree=1., device='cuda:0')
        started = time.monotonic()
        with threadpool_limits(limits=1):
            model.fit(np.asarray([e['x'] for e in examples]), np.asarray([e['label'] for e in examples]))
        proof = validate_gpu_fit(model, build_info)
        proof.update(training_example_ids=[e['example_id'] for e in examples],
                     elapsed_seconds=time.monotonic()-started, parameter=parameter)
        fit_proofs.append(proof)
        lab.write(output / 'gpu-fit-proofs.json', {'synthetic': True, 'fits': fit_proofs})
        return model

    def predict(method, model, examples, *, news=False):
        if method != 'gradient_boosting':
            return original_predict(method, model, examples, news=news)
        # DMatrix avoids sklearn inplace_predict's mismatched CPU-array/device
        # path; the fitted CUDA device is independently verified above.
        result = model.get_booster().predict(xgb.DMatrix(np.asarray([e['x'] for e in examples])))
        if not np.isfinite(result).all():
            raise ValueError('nonfinite_GPU_predictions')
        return np.maximum(0., result)

    # Images carry a reviewed source manifest, not a fabricated .git directory.
    # Only the runner's provenance lookup is adapted; the source is explicit.
    def commit_lookup(command, text=False):
        if command != ['git', 'rev-parse', 'HEAD']:
            raise ValueError('unexpected_runner_subprocess')
        return source_commit + '\n'
    lab.subprocess = SimpleNamespace(check_output=commit_lookup)
    forecasting.fit_candidate, forecasting.predict = fit, predict
    try:
        result = lab.run(output, expected_dataset=DATASET_SHA, expected_code=PINNED_RUNNER_SHA)
    finally:
        forecasting.fit_candidate, forecasting.predict = original_fit, original_predict
    if len(fit_proofs) != 5:
        raise RuntimeError('expected_five_actual_GPU_fits_in_twelve_fit_experiment')
    diagnostics = {}
    for family, record in result['family_results'].items():
        previous = reference['family_results'][family]['validation_choice_simulation_only']
        diagnostics[family] = record['validation_choice_simulation_only']
        record['gpu_validation_choice_diagnostic'] = record['validation_choice_simulation_only']
        record['validation_choice_simulation_only'] = previous
        record['selection_authority'] = 'previous_SY2_validation_choice; no_test_reselection_or_promotion'
        for split, methods in record['metrics_by_split'].items():
            for method, metrics in methods.items():
                metrics['device'] = 'cuda:0' if method == 'gradient_boosting' else 'cpu'
                old = reference['family_results'][family]['metrics_by_split'][split][method]
                metrics['mae_delta_vs_local_CPU_reference'] = metrics['mae'] - old['mae']
    result.update(execution_location='runpod_gpu', paid_cost_usd=None,
        source_commit_origin='verified_image_manifest; no_in_container_git_history',
        gpu_fit_proofs=fit_proofs, xgboost_build_info=build_info, gpu_inventory=gpu_inventory,
        cpu_methods=['no_change', 'seasonal', 'ridge'], selected_normal_runtime_model=None,
        normal_serving_eligible=False, previous_selection_preserved=True,
        gpu_validation_choice_diagnostics=diagnostics)
    result['pilot']['device'] = 'mixed: Ridge CPU; XGBoost cuda:0'
    diagnostic = json.loads((output/'frozen-selection.json').read_text())
    lab.write(output/'gpu-frozen-selection-diagnostic.json', diagnostic)
    lab.write(output/'frozen-selection.json', {'synthetic': True, 'normal_serving_eligible': False,
              'selection': previous_selection, 'authority': 'previous_SY2_validation; no_new_runtime_selection'})
    result['gpu_diagnostic_selection_sha256'] = result['frozen_selection_sha256']
    result['frozen_selection_sha256'] = lab.sha(output/'frozen-selection.json')
    for metadata in result['artifacts']:
        metadata['training_device'] = 'cuda:0' if metadata['method'] == 'gradient_boosting' else 'cpu'
        path = output / metadata['artifact']
        lab.write(path.with_suffix('.metadata.json'), metadata)
        if metadata['method'] == 'gradient_boosting':
            import joblib
            model = joblib.load(path)
            model.get_booster().save_model(path.with_suffix('.ubj'))
    lab.write(output / 'results.json', result)
    return result
