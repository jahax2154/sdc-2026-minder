"""Actual owner-scoped notice read ordering; explicit synthetic timestamps, no worker/model."""
import json
from pathlib import Path
import tempfile
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.integration_cli import wsgi_request


def main():
    out = Path('ml/artifacts/session-a/product/morning')
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        app, _ = build('A', database=Path(tmp) / 'notices.sqlite3', role_ids=['onet:15-1252.00'])
        session = wsgi_request(app, 'POST', '/api/session', {})[1]
        other = wsgi_request(app, 'POST', '/api/session', {})[1]
        with app.store.transaction() as db:
            for owner, identifier, stamp in (
                    (session['profile_id'], 'a-old', '2026-10-24T10:00:00+08:00'),
                    (session['profile_id'], 'z-new', '2026-10-24T03:00:00Z'),
                    (session['profile_id'], '0-unknown', None),
                    (other['profile_id'], 'foreign', '2026-10-24T10:00:00Z')):
                value = dict(event_id=identifier, summary='Synthetic ' + identifier + ' notice')
                if stamp:
                    value['created_at'] = stamp
                db.execute('INSERT INTO notices VALUES(?,?,?)', (owner, identifier, json.dumps(value)))
        status, result = wsgi_request(app, 'GET', '/api/agents', {}, session['token'])
        assert status == 200
        order = [n['event_id'] for n in result['notices']]
        report = dict(runtime_revision=app.runtime_revision, actual_WSGI=True,
            explicit_synthetic_notice_fixture=True, order=order, expected=['z-new', 'a-old', '0-unknown'],
            other_owner_excluded='foreign' not in order, provider_calls=0,
            deployment_scheduler_verified=result['deployment_scheduler_verified'])
        (out / ('ux-notice-order-' + ('pass' if order == report['expected'] else 'failure') + '.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        assert order == report['expected'], 'Home latest update would select an older notice'


if __name__ == '__main__':
    main()
