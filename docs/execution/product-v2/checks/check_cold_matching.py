"""One fresh application-process matching measurement; no provider invocation."""
import argparse
import json
from pathlib import Path
import tempfile
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=('sparse', 'adequate'), required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    from minder_ml.intelligence.product_runtime import build
    from minder_ml.intelligence.integration_cli import wsgi_request, provisional_demo_profile
    from minder_ml.intelligence.role_fit import reference
    out = Path('ml/artifacts/session-a/product/morning')
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        app, _ = build('A', database=Path(tmp) / 'cold.sqlite3')
        startup_ms = (time.perf_counter() - start) * 1000
        token = wsgi_request(app, 'POST', '/api/session', {})[1]['token']
        profile = (dict(synthetic=True, onboarding=dict(stage='studying', objective='fit',
                   context='Fictional computing student')) if args.case == 'sparse' else
                   provisional_demo_profile(levels=(4,) * len(reference()['skills'])))
        status, _ = wsgi_request(app, 'PUT', '/api/profile',
            dict(profile=profile, expected_version=None), token)
        assert status == 200
        begin = time.perf_counter()
        status, result = wsgi_request(app, 'POST', '/api/product/views/career-match', {}, token)
        elapsed_ms = (time.perf_counter() - begin) * 1000
        assert status == 200
        report = dict(runtime_revision=app.runtime_revision, case=args.case,
            measurement='Fresh Python application process, first global WSGI source request; OS file caches uncontrolled, not hosted or network/browser latency',
            startup_ms=round(startup_ms, 3), first_request_ms=round(elapsed_ms, 3),
            provider_calls=0, coverage=result['data']['recommendation']['coverage'])
        (out / ('cold-matching-' + args.case + '.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
