"""Bounded local payload/budget/artifact controls. No automatic provisioning."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen

SECRET = Path(__file__).resolve().parents[5] / '.env.runpod.local'
ENDPOINT_NAME = 'minder-b-gpu-once-20261024'
PAYLOAD = {'input': {'experiment_id': 'minder-synthetic-gpu-20261024-once',
    'dataset_sha256': 'b7aa327d30220b27a2236476b5c51d45d04deb16d9bfb009cc2fcca81a01880b',
    'require_gpu': True}, 'policy': {'executionTimeout': 180000, 'ttl': 300000}}


def load_secret(path=SECRET, *, require_endpoint=True, require_image=True):
    if path.stat().st_mode & 0o077:
        raise ValueError('private_config_must_be_mode_600')
    result = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        key, value = line.split('=', 1)
        if key not in ('RUNPOD_API_KEY', 'RUNPOD_ENDPOINT_ID', 'RUNPOD_IMAGE'):
            raise ValueError('unexpected_private_config_key')
        value = value.strip()
        if len(value)>=2 and value[0]==value[-1] and value[0] in ('\"', "'"):
            value = value[1:-1]
        result[key] = value
    if not result.get('RUNPOD_API_KEY'):
        raise ValueError('private_key_not_configured')
    if require_endpoint:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', result.get('RUNPOD_ENDPOINT_ID', '')):
            raise ValueError('private_endpoint_not_configured')
        if require_image and not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}', result.get('RUNPOD_IMAGE', '')):
            raise ValueError('final_image_digest_required')
    return result


def budget_check(evidence):
    required = ('user_confirmed_credits_and_key', 'balance_verified', 'image_pull_verified',
                'endpoint_settings_verified', 'provider_attempt_bound_verified',
                'provider_hard_stop_verified', 'artifact_roundtrip_verified',
                'billable_bound_includes_initialization_test_retries_cleanup')
    if not all(evidence.get(k) is True for k in required):
        raise ValueError('live_preflight_incomplete; no_submission')
    if evidence.get('automatic_topup') is not False or evidence.get('billing_upgrade') is not False:
        raise ValueError('topup_or_upgrade_not_allowed')
    attempts = evidence.get('max_provider_attempts')
    if type(attempts) is not int or attempts < 1 or evidence.get('workers_min') != 0 or evidence.get('workers_max') != 1 or evidence.get('gpu_count') != 1:
        raise ValueError('one_worker_one_GPU_and_finite_verified_attempt_bound_required')
    if evidence['balance_usd'] < 2 or evidence['existing_billable_workers'] != 0:
        raise ValueError('balance_or_existing_worker_spend_not_safe')
    rate = evidence['verified_rate_usd_per_second']
    hard_seconds = evidence['verified_total_billable_seconds_bound']
    ancillary = evidence['ancillary_and_billing_rounding_usd_bound']
    if not (0 < rate and 0 < hard_seconds <= 900 and ancillary >= 0):
        raise ValueError('invalid_quote_or_hard_time_bound')
    upper = rate * hard_seconds + ancillary
    if upper > 2:
        raise ValueError('USD2_total_bound_exceeded')
    return upper


def retrieve(output, destination):
    raw = base64.b64decode(output['artifact_base64'], validate=True)
    if len(raw) > 2*1024*1024 or hashlib.sha256(raw).hexdigest() != output['artifact_sha256']:
        raise ValueError('artifact_checksum_or_size_mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        items = archive.infolist()
        if len(items)>100 or sum(i.file_size for i in items)>10*1024*1024:
            raise ValueError('uncompressed_artifact_bound_exceeded')
        for item in items:
            name = PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in item.filename or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('unsafe_artifact_path')
        destination.mkdir(parents=True, exist_ok=True)
        for item in items:
            path = destination / item.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(item))
    (destination/'retrieved-archive.zip').write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def api(method, url, secret, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(url, data=body, method=method,
                      headers={'Authorization': 'Bearer '+secret['RUNPOD_API_KEY'], 'Content-Type': 'application/json'})
    # No HTTP submission retry; a timeout after POST is ambiguous and must not
    # cause another paid submission. Both Serverless and verified GraphQL
    # authentication use the header; no production URL contains the key.
    try:
        with urlopen(request, timeout=30) as response:
            data = response.read(8*1024*1024 + 1)
    except Exception as exc:
        # Never echo provider error bodies or private authentication material.
        raise RuntimeError('provider_request_failed:' + type(exc).__name__) from None
    if len(data)>8*1024*1024:
        raise ValueError('API_response_bound_exceeded')
    return json.loads(data)


def management(command, secret):
    endpoint = secret['RUNPOD_ENDPOINT_ID']
    listed = api('POST', 'https://api.runpod.io/graphql',
        secret, {'query':'query { myself { endpoints { id name gpuIds templateId workersMin workersMax idleTimeout pods { desiredStatus } } } }'})
    if listed.get('errors'):
        raise RuntimeError('management_access_not_verified')
    matches = [e for e in listed['data']['myself']['endpoints'] if e['id']==endpoint]
    if len(matches)!=1:
        raise ValueError('named_endpoint_not_found; no_management_mutation')
    own = matches[0]
    if command == 'inspect-endpoint':
        return own
    if own['name'] != ENDPOINT_NAME:
        raise ValueError('refuse_mutation_of_non_experiment_endpoint')
    if command == 'shutdown':
        query = 'mutation { saveEndpoint(input: { id: '+json.dumps(endpoint)+', name: '+json.dumps(own['name'])+', gpuIds: '+json.dumps(own['gpuIds'])+', templateId: '+json.dumps(own['templateId'])+', workersMin: 0, workersMax: 0 }) { id workersMin workersMax } }'
    else:
        if own['workersMin']!=0 or own['workersMax']!=0 or own['pods']:
            raise ValueError('zero_worker_counts_and_no_pods_required_before_delete')
        query = 'mutation { deleteEndpoint(id: '+json.dumps(endpoint)+') }'
    result = api('POST', 'https://api.runpod.io/graphql', secret, {'query':query})
    if result.get('errors'):
        raise RuntimeError('management_mutation_failed; verify_cleanup_manually')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['account', 'payload', 'budget', 'submit', 'status', 'cancel', 'retrieve',
                                          'inspect-endpoint', 'shutdown', 'delete-endpoint'])
    parser.add_argument('--preflight', type=Path)
    parser.add_argument('--receipt-dir', type=Path, default=Path('ml/artifacts/session-b/gpu-live'))
    parser.add_argument('--job-id')
    parser.add_argument('--response', type=Path)
    args = parser.parse_args()
    if args.command == 'payload':
        print(json.dumps(PAYLOAD, indent=2)); return
    if args.command == 'account':
        secret = load_secret(require_endpoint=False)
        response = api('POST', 'https://api.runpod.io/graphql', secret, {'query':
            'query { myself { clientBalance currentSpendPerHr githubAccountInfo { username } isAutoPayEnabled stripeAutoReloadAmount endpoints { id name workersMin workersMax pods { desiredStatus } } pods { desiredStatus } } }'})
        if response.get('errors'):
            raise RuntimeError('account_access_or_schema_check_failed')
        own = response['data']['myself']
        args.receipt_dir.mkdir(parents=True,exist_ok=True)
        safe = {'balance_usd':own['clientBalance'], 'current_spend_per_hour':own['currentSpendPerHr'],
                'github_connected':bool(own['githubAccountInfo']), 'automatic_payment_enabled':own['isAutoPayEnabled'],
                'endpoint_count':len(own['endpoints']), 'pod_count':len(own['pods']),
                'dedicated_endpoints':[e for e in own['endpoints'] if e['name']==ENDPOINT_NAME]}
        (args.receipt_dir/'account-sanitized.json').write_text(json.dumps(safe,indent=2)+'\n')
        print(json.dumps(safe)); return
    if args.command in ('budget', 'submit'):
        if not args.preflight:
            parser.error('live verified preflight file required')
        evidence = json.loads(args.preflight.read_text())
        upper = budget_check(evidence)
        if args.command == 'budget':
            print(json.dumps({'cost_upper_usd': upper, 'billable_action': False})); return
    if args.command == 'retrieve':
        response = json.loads(args.response.read_text())
        digest = retrieve(response['output'], args.receipt_dir / 'artifacts')
        print(json.dumps({'artifact_sha256': digest, 'retrieved': True})); return
    # Management/cancellation must remain usable during a failed image build;
    # only experiment submission needs the final immutable image reference.
    secret = load_secret(require_image=args.command == 'submit')
    base = 'https://api.runpod.ai/v2/' + secret['RUNPOD_ENDPOINT_ID']
    args.receipt_dir.mkdir(parents=True, exist_ok=True)
    if args.command in ('inspect-endpoint', 'shutdown', 'delete-endpoint'):
        result = management(args.command, secret)
    elif args.command == 'submit':
        if evidence.get('verified_endpoint_id') != secret['RUNPOD_ENDPOINT_ID'] or evidence.get('verified_image_digest') != secret['RUNPOD_IMAGE']:
            raise ValueError('live_preflight_not_bound_to_configured_endpoint_and_image')
        # Persist intent BEFORE network I/O. Unknown outcome blocks repeats.
        intent = SECRET.parent / 'ml/artifacts/session-b/gpu-live/submission-intent.json'
        intent.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(intent, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        with os.fdopen(fd,'w') as file:
            json.dump({'experiment_id':PAYLOAD['input']['experiment_id'], 'cost_upper_usd':upper,
                       'UTC_submitted':datetime.now(timezone.utc).isoformat(),
                       'endpoint_id':secret['RUNPOD_ENDPOINT_ID'], 'image':secret['RUNPOD_IMAGE'],
                       'preflight_sha256':hashlib.sha256(args.preflight.read_bytes()).hexdigest()}, file)
        result = api('POST', base+'/run', secret, PAYLOAD)
    else:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', args.job_id or ''):
            parser.error('valid actual job ID required')
        result = api('POST' if args.command=='cancel' else 'GET', base+'/'+args.command+'/'+args.job_id, secret)
    (args.receipt_dir/(args.command+'-response.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('id','status') if k in result}))


if __name__ == '__main__':
    main()
