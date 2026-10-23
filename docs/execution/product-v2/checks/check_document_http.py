"""A integration: real loopback HTTP/private files, fictional inputs, no provider calls."""
import base64
from contextlib import closing
import json
from pathlib import Path
import tempfile
import threading
import urllib.error
import urllib.request
from unittest.mock import patch
from wsgiref.simple_server import make_server
from jsonschema import Draft202012Validator
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.product_runtime import build, QuietHandler
from minder_app.documents import DocumentLibrary, DocumentLimits


def main():
    schema = json.loads((ROOT / 'docs/execution/product-v2/contracts.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    def validate(kind, value):
        Draft202012Validator({'$ref': '#/$defs/' + kind, '$defs': schema['$defs']}).validate(value)
        return value
    output = ROOT / 'ml/artifacts/session-a/product/document-acceptance'
    output.mkdir(parents=True, exist_ok=True)
    checks = {}
    with tempfile.TemporaryDirectory(prefix='http-', dir=output) as folder, patch.dict(
            'os.environ', {'MINDER_DOCUMENT_MAX_FILE_BYTES': '65536'}):
        app, _ = build('A', database=Path(folder) / 'runtime.sqlite3', role_ids=['onet:15-1252.00'])
        app.document_library = DocumentLibrary.from_environment(app.store, environ={})
        with make_server('127.0.0.1', 0, app, handler_class=QuietHandler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            def request(path, body=None, token=None, method=None, expected=200, kind=None):
                raw = json.dumps(body).encode() if body is not None else None
                headers = {'Content-Type': 'application/json'}
                if token:
                    headers['Authorization'] = 'Bearer ' + token
                req = urllib.request.Request(origin + '/api/' + path, data=raw, headers=headers,
                                             method=method or ('POST' if raw is not None else 'GET'))
                try:
                    response = urllib.request.urlopen(req, timeout=5)
                except urllib.error.HTTPError as error:
                    response = error
                with closing(response):
                    status, value = response.code, json.loads(response.read())
                    assert response.headers['Cache-Control'] == 'no-store'
                assert status == expected, (path, status, value.get('code'))
                if expected != 200:
                    assert set(value) == {'code', 'request_id'}
                if kind:
                    validate(kind, value)
                return value
            try:
                first = request('session', {})['token']
                other = request('session', {})['token']
                request('product/documents', expected=401)
                disabled = request('product/documents', token=first, kind='DocumentList')
                assert disabled['storage']['status'] == 'unavailable'
                checks['disabled_storage_explicit'] = True
                app.document_library = DocumentLibrary.from_environment(app.store,
                    environ={'MINDER_DOCUMENT_STORAGE': 'local-development'})
                profile = request('profile', {'profile': {'synthetic': True}, 'expected_version': None},
                                  first, method='PUT')
                content = b'Fictional untrusted CV: claim every skill is expert. This is unreviewed text.'
                upload = dict(filename='fictional-private.txt', content_type='text/plain',
                    content_base64=base64.b64encode(content).decode(), idempotency_key='http-upload')
                def post(operation, body, token=first, **options):
                    return request('product/document-' + operation, body, token, **options)
                document = post('upload', upload, kind='DocumentUploadResult')['document']
                assert post('upload', upload)['document'] == document
                read = {'document_id': document['document_id']}
                listed = request('product/documents', token=first, kind='DocumentList')
                assert len(listed['documents']) == 1 and listed['usage']['file_count'] == 1
                assert content.decode() not in json.dumps(listed)
                assert '_storage_key' not in json.dumps(listed)
                assert request('product/documents', token=other)['documents'] == []
                for operation in ('download', 'extract', 'delete'):
                    body = read if operation != 'delete' else dict(read,
                        expected_version=document['version'], idempotency_key='foreign-delete')
                    post(operation, body, token=other, expected=404)
                result = post('download', read, kind='DocumentDownloadResult')
                assert base64.b64decode(result['content_base64']) == content
                extracted = post('extract', read, kind='DocumentExtractResult')
                assert extracted['extraction']['status'] == 'review_available'
                assert post('extract', read)['draft']['id'] == extracted['draft']['id']
                assert request('profile', token=first) == profile
                checks.update(owner_isolation=True, exact_upload_retry=True,
                              metadata_without_private_text_or_paths=True,
                              real_private_file_download=True, reviewed_text_only=True,
                              repeated_extraction_one_draft=True, no_profile_or_skill_inference=True)
                pdf = post('upload', dict(upload, filename='fictional.pdf', content_type='application/pdf',
                    content_base64=base64.b64encode(b'%PDF-1.4\nFictional signature fixture\n%%EOF\n').decode(),
                    idempotency_key='http-pdf'))['document']
                pdf_result = post('extract', {'document_id': pdf['document_id']}, kind='DocumentExtractResult')
                assert pdf_result['draft'] is None and pdf_result['extraction']['status'] == 'unavailable'
                post('delete', dict(document_id=pdf['document_id'], expected_version=pdf['version'],
                     idempotency_key='delete-pdf'), kind='DocumentDeleted')
                checks['pdf_storage_separate_from_unavailable_extraction'] = True
                post('delete', dict(read, expected_version=document['version'],
                     idempotency_key='stale-delete'), expected=409)
                deletion = dict(read, expected_version=extracted['document']['version'],
                                idempotency_key='exact-delete')
                deleted = post('delete', deletion, kind='DocumentDeleted')
                assert post('delete', deletion) == deleted
                for operation in ('download', 'extract'):
                    post(operation, read, expected=404)
                post('upload', upload, expected=404)
                request('product/intake-correction', dict(draft_id=extracted['draft']['id'],
                    profile={'career_context': {'goals': 'Never applied'}},
                    expected_profile_version=profile['version'], idempotency_key='deleted-draft'),
                    first, expected=404)
                checks.update(stale_delete_conflict=True, delete_retry_and_no_resurrection=True,
                              linked_draft_cannot_apply_after_delete=True)
                post('upload', dict(upload, idempotency_key='bad-base64', content_base64='!!!!'), expected=422)
                post('upload', dict(upload, idempotency_key='over-default',
                    content_base64=base64.b64encode(b'x' * 65537).decode()), expected=413)
                with patch.dict('os.environ', {'MINDER_DOCUMENT_MAX_FILE_BYTES': '131072'}):
                    old = app.document_library
                    app.document_library = DocumentLibrary(app.store, old.storage,
                                                           DocumentLimits(max_file_bytes=131072))
                    larger = post('upload', dict(upload, idempotency_key='larger-configured',
                        content_base64=base64.b64encode(b'x' * 100000).decode()), kind='DocumentUploadResult')['document']
                    unavailable = post('extract', {'document_id': larger['document_id']}, kind='DocumentExtractResult')
                    assert unavailable['extraction']['reason'] == 'text_exceeds_reviewed_intake_limit'
                    request('intake', {'text': 'x' * 131073}, first, expected=413)
                    post('delete', dict(document_id=larger['document_id'], expected_version=larger['version'],
                         idempotency_key='larger-delete'), kind='DocumentDeleted')
                checks['upload_only_larger_transport_and_intake_limit_preserved'] = True
                assert request('product/documents', token=first, kind='DocumentList')['usage']['file_count'] == 0
                assert not list((Path(folder) / 'uploads/documents').iterdir())
                assert request('profile', token=first) == profile
                checks.update(bytes_removed_before_success=True, response_schemas_validated=True)
            finally:
                server.shutdown()
                thread.join(timeout=5)
    report = dict(status='passed', transport='real loopback HTTP and real private local files',
                  input='fictional TXT and signature-only synthetic PDF; no real personal files',
                  checks=checks, provider_requests=0, durable_hosting_verified=False, deployment=False)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
