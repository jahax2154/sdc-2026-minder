"""Single immutable RunPod handler; no account credentials belong in the image."""
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[5]
EXPERIMENT = 'minder-synthetic-gpu-20261024-once'
DISPLAY = 'Simulated scenario — generated assumptions, not observed Malaysian demand.'
MAX_ARCHIVE = 2 * 1024 * 1024


def utc():
    return datetime.now(timezone.utc).isoformat()


def validate_payload(job):
    from gpu_synthetic_adapter import DATASET_SHA
    if not isinstance(job, dict) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', job.get('id', '')):
        raise ValueError('invalid_job_envelope')
    expected = {'experiment_id': EXPERIMENT, 'dataset_sha256': DATASET_SHA, 'require_gpu': True}
    if job.get('input') != expected or job['input'].get('require_gpu') is not True:
        raise ValueError('immutable_payload_required')
    return expected


def verify_manifest(root):
    manifest = json.loads((root / 'gpu-image-manifest.json').read_text())
    if manifest.get('uncommitted_preparation') is not False:
        raise ValueError('uncommitted_preparation_cannot_run_live')
    for name, expected in manifest['files'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('image_content_checksum_mismatch:' + name)
    return manifest


def package(output):
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(output).as_posix())
    data = memory.getvalue()
    if len(data) > MAX_ARCHIVE:
        raise ValueError('artifact_response_size_exceeds_bound')
    return {'artifact_encoding': 'base64_zip', 'artifact_sha256': hashlib.sha256(data).hexdigest(),
            'artifact_bytes': len(data), 'artifact_base64': base64.b64encode(data).decode()}


def handler(job):
    start = utc()
    try:
        validate_payload(job)
        manifest = verify_manifest(ROOT)
    except (ValueError, KeyError, OSError) as exc:
        return {'synthetic': True, 'status': 'rejected', 'reason': str(exc), 'gpu_proof': False}
    output = ROOT / 'ml/artifacts/session-b/synthetic-lab/gpu-once'
    output.mkdir(parents=True, exist_ok=True)
    # Local receipt prevents replay on this worker. Cross-worker requeue remains
    # a provider-side preflight condition, not a claimed exactly-once guarantee.
    try:
        fd = os.open(output / 'started.receipt', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as receipt:
            receipt.write(job['id'])
    except FileExistsError:
        return {'synthetic': True, 'status': 'duplicate_rejected', 'gpu_proof': False}
    status = 'failed'
    try:
        command = [sys.executable, str(Path(__file__)), '--experiment-child', manifest['source_commit']]
        with (output / 'execution.stdout.txt').open('w') as log:
            completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        status = 'completed' if completed.returncode == 0 else 'failed'
        if status == 'completed':
            result = json.loads((output/'results.json').read_text())
            proofs = result['gpu_fit_proofs']
            if len(proofs) != 5 or not all(p['effective_device'].startswith('cuda') and
                'gpu' in p['updater'] and p['boosted_rounds'] == 48 for p in proofs):
                raise ValueError('child_did_not_supply_actual_GPU_fit_proofs')
            result.update(runpod_job_id=job['id'], UTC_start=start, UTC_end=utc())
            (output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    except subprocess.TimeoutExpired:
        status = 'timed_out'
    except Exception as exc:
        (output / 'execution-error.txt').write_text(type(exc).__name__ + '\n')
        status = 'failed'
    finally:
        record = {'synthetic': True, 'normal_serving_eligible': False, 'status': status,
                  'job_id': job['id'], 'UTC_start': start, 'UTC_end': utc(),
                  'source_commit': manifest['source_commit'], 'image_manifest': manifest,
                  'paid_cost_usd': None, 'billing': 'operator_must_reconcile_actual_charges',
                  'shutdown': 'provider_scale_to_zero_and_endpoint_cleanup_must_be_verified'}
        (output / 'job-record.json').write_text(json.dumps(record, indent=2) + '\n')
    # Artifact bytes are returned before ephemeral worker teardown. Failure logs
    # and partial fit proofs are returned too; no SDK exception/retry request.
    try:
        return dict(synthetic=True, display_label=DISPLAY, normal_serving_eligible=False, status=status,
                    gpu_proof=status == 'completed', job_id=job['id'], **package(output))
    except Exception as exc:
        return {'synthetic': True, 'status': 'artifact_return_failed', 'gpu_proof': False,
                'job_id': job['id'], 'reason': type(exc).__name__}


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--experiment-child':
        from gpu_synthetic_adapter import execute
        execute(ROOT, ROOT / 'ml/artifacts/session-b/synthetic-lab/gpu-once', sys.argv[2])
    else:
        import runpod
        runpod.serverless.start({'handler': handler})
