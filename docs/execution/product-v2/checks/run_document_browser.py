"""Run F's unmodified document browser checks on a disposable A-only local server."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from wsgiref.simple_server import make_server
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.product_runtime import build, web_app, QuietHandler
from minder_app.documents import DocumentLibrary


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-retry', action='store_true', help='Explicit transport-loss fault case, not live-provider evidence')
    args = parser.parse_args()
    output = ROOT / ('ml/artifacts/session-a/product/document-review-retry' if args.review_retry
                     else 'ml/artifacts/session-a/product/document-browser')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='runtime-', dir=output) as folder:
        app, _ = build('A', database=Path(folder) / 'runtime.sqlite3')
        # Explicit test-only configuration, not a persistent runtime/env-file edit.
        app.document_library = DocumentLibrary.from_environment(app.store,
            environ={'MINDER_DOCUMENT_STORAGE': 'local-development'})
        with make_server('127.0.0.1', 0, web_app(app), handler_class=QuietHandler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            # Provider credentials remain in the backend. No secret environment
            # variables or provider config path are inherited by the browser runner.
            env = {key: value for key, value in os.environ.items() if key in
                ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'PLAYWRIGHT_BROWSERS_PATH',
                 'MINDER_PLAYWRIGHT_MODULE')}
            env.update(MINDER_PRODUCT_BASE_URL='http://127.0.0.1:' + str(server.server_port),
                       MINDER_BROWSER_OUTPUT_DIR=str(output))
            try:
                script = ('docs/execution/product-v2/checks/check_review_retry.cjs' if args.review_retry
                          else 'apps/frontend-product/tests/documents.cjs')
                result = subprocess.run(['node', script],
                    cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
                (output / 'browser.log').write_text(result.stdout + result.stderr)
                assert result.returncode == 0, 'document_browser_failed_see_private_log'
                checks = json.loads((output / ('document-review-retry.json' if args.review_retry
                                               else 'minder-f-documents.json')).read_text())
                if args.review_retry:
                    assert checks['stale_review_replayed'] is False
                else:
                    assert checks['explicit_review_no_mastery'] and checks['delete_library_empty']
                    assert checks['page_errors'] == []
            finally:
                server.shutdown()
                thread.join(timeout=5)
    report = dict(status='passed', runner='Unmodified F documents.cjs; environment base/output only',
                  checks=checks, development_storage='Explicit only in disposable A test server',
                  persistent_runtime_config_changed=False, provider_calls=0,
                  durable_hosting_verified=False, deployment=False)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
