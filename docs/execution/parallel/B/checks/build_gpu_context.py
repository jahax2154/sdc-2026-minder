"""Create a credential-free Docker context from explicit tracked source inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[5]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-preparation-check', action='store_true')
    args = parser.parse_args()
    output = ROOT / 'ml/artifacts/session-b/gpu-preparation/context'
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    selected = [p for p in tracked if (p.startswith('ml/src/') and p.endswith('.py'))
                or (p.startswith('contracts/') and p.endswith('.json'))]
    selected += ['ml/data/market/' + name for name in ('snapshot.v1.json', 'mapping.v1.json',
        'published-role-observations.v1.json', 'current-public-evidence.v1.json',
        'serving-registry.v1.json', 'forecast-dataset.v1.json')]
    selected += ['docs/execution/parallel/source_snapshot.v1.json']
    selected += ['docs/execution/parallel/B/' + name for name in (
        'synthetic-results.v1.json', 'checks/synthetic_market_experiment.py',
        'synthetic-runpod-job.v1.json', 'synthetic-runpod-requirements.v1.txt',
        'checks/run_synthetic_job.py', 'checks/gpu_synthetic_adapter.py', 'checks/gpu_worker.py',
        'checks/gpu-requirements.v1.txt')]
    selected += ['ml/data/market/synthetic-lab/scenario-spec.v1.json']
    if not args.local_preparation_check:
        if any(p not in tracked for p in selected):
            raise ValueError('commit_preparation_before_live_image_build')
        subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', *selected], cwd=ROOT, check=True)
    runtime = output / 'runtime'
    extras = {p.relative_to(runtime).as_posix() for p in runtime.rglob('*') if p.is_file()} - set(selected) - {'gpu-image-manifest.json'}
    if extras:
        raise ValueError('unexpected_existing_context_files; use_a_reviewed_clean_context')
    for name in selected:
        dest = output / 'runtime' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    manifest = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'uncommitted_preparation': args.local_preparation_check,
                'files': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(selected)},
                'private_inputs_included': False}
    (output/'runtime/gpu-image-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    shutil.copyfile(ROOT/'docs/execution/parallel/B/checks/GPU.Dockerfile', output/'Dockerfile')
    print(json.dumps({'context': str(output), 'source_commit': manifest['source_commit'],
                      'files': len(selected), 'docker_build_executed': False,
                      'private_inputs_included': False, 'local_preparation_check': args.local_preparation_check}))


if __name__ == '__main__':
    main()
