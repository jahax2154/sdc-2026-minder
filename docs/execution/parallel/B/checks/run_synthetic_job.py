"""Execute an already provisioned bounded CPU simulation; never provisions/bills."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[5]
    os.chdir(root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--execution-location', choices=['local_cpu', 'runpod_cpu'], default='local_cpu')
    parser.add_argument('--runpod-job-id')
    parser.add_argument('--output-dir', type=Path,
                        default=Path('ml/artifacts/session-b/synthetic-lab/runpod-v1'))
    args = parser.parse_args()
    if args.execution_location == 'runpod_cpu' and not args.runpod_job_id:
        parser.error('RunPod execution requires the actual operator-captured job/resource ID')
    if args.execution_location == 'local_cpu' and args.runpod_job_id:
        parser.error('A local replay cannot claim a RunPod job ID')
    spec = json.loads(Path('docs/execution/parallel/B/synthetic-runpod-job.v1.json').read_text())
    for name, expected in spec['immutable_inputs'].items():
        if digest(Path(name)) != expected:
            raise ValueError('code_or_input_checksum_mismatch:' + name)
    subprocess.run(['git', 'merge-base', '--is-ancestor', spec['code_commit'], 'HEAD'], check=True)
    subprocess.run(['git', 'diff', '--quiet', spec['code_commit'], 'HEAD', '--',
                    'ml/src', 'ml/data/market', spec['runner']], check=True)
    for name, version in spec['dependencies'].items():
        if importlib.metadata.version(name) != version:
            raise ValueError('dependency_version_mismatch:' + name)
    if sys.version_info[:2] != (3, 9):
        raise ValueError('reference_replay_requires_CPython_3_9; choose_tested_image_before_paid_launch')
    output = args.output_dir.resolve()
    if not output.is_relative_to(root / 'ml/artifacts/session-b/synthetic-lab'):
        raise ValueError('synthetic_output_namespace_required')
    if args.preflight_only:
        print(json.dumps({'preflight': 'passed', 'fits': 0, 'synthetic': True,
                          'provisions_resources': False, 'launches_paid_jobs': False}))
        return
    output.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PYTHONPATH='ml/src', OMP_NUM_THREADS='1',
                       OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='',
                       PYTHONWARNINGS='error::RuntimeWarning')
    commands = [[sys.executable, spec['runner'], 'generate', '--output-dir', str(output)],
                [sys.executable, spec['runner'], 'run', '--output-dir', str(output),
                 '--expected-dataset-sha256', spec['dataset_sha256'],
                 '--expected-code-sha256', spec['immutable_inputs'][spec['runner']]]]
    started = time.monotonic()
    status = 'failed'
    try:
        with (output / 'execution.stdout.txt').open('w') as log:
            for command in commands:
                subprocess.run(command, check=True, env=environment, stdout=log,
                               stderr=subprocess.STDOUT,
                               timeout=max(1, spec['limits']['process_timeout_seconds'] - (time.monotonic() - started)))
        result = json.loads((output / 'results.json').read_text())
        result.update(execution_location=args.execution_location, runpod_job_id=args.runpod_job_id,
                      paid_cost_usd=None if args.execution_location == 'runpod_cpu' else 0)
        (output / 'results.json').write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + '\n')
        reference = json.loads(Path('docs/execution/parallel/B/synthetic-results.v1.json').read_text())
        assert result['dataset_sha256'] == spec['dataset_sha256']
        for family in ('role', 'skill'):
            for split in ('train', 'validation', 'test', 'robustness'):
                for method, metrics in result['family_results'][family]['metrics_by_split'][split].items():
                    expected = reference['family_results'][family]['metrics_by_split'][split][method]
                    for metric in ('mae', 'rmse', 'wape'):
                        if metrics[metric] is None or expected[metric] is None:
                            assert metrics[metric] == expected[metric]
                        else:
                            assert abs(metrics[metric] - expected[metric]) <= 1e-5
        status = 'passed'
    finally:
        evidence = {'synthetic': True, 'normal_serving_eligible': False, 'status': status,
                    'elapsed_seconds': time.monotonic() - started,
                    'code_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    'files': {str(p.relative_to(output)): digest(p) for p in output.rglob('*') if p.is_file()},
                    'execution_location': args.execution_location, 'paid_job_id': args.runpod_job_id,
                    'billing': 'not_measured_by_this_script; operator must record actual charges and termination'}
        (output / 'execution-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print(json.dumps({'synthetic': True, 'status': status, 'output': str(output)}))


if __name__ == '__main__':
    main()
