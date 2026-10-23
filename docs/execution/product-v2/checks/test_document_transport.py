"""A-owned transport tests; stub D storage intentionally, no files/provider calls."""
import base64
from io import BytesIO
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from support import AppCase
from minder_app import product_routes


class DocumentTransportTests(AppCase):
    def http(self, path, body, *, token=True, method='POST'):
        raw = json.dumps(body).encode()
        captured = []
        answer = self.app(dict(REQUEST_METHOD=method, PATH_INFO=path,
            CONTENT_LENGTH=str(len(raw)), **{'wsgi.input': BytesIO(raw)},
            HTTP_AUTHORIZATION='Bearer ' + self.session['token'] if token else ''),
            lambda status, headers: captured.append((int(status.split()[0]), dict(headers))))
        self.assertEqual(captured[0][1]['Cache-Control'], 'no-store')
        return captured[0][0], json.loads(b''.join(answer))

    def test_upload_registration_and_unavailable_owner_scope(self):
        code, caps = self.http('/api/product/capabilities', {}, method='GET')
        documents = [x for x in caps['operations'] if x['module'] == 'documents']
        self.assertEqual(len(documents), 5)
        self.assertTrue(all(x['owner'] == 'D' for x in documents))
        if product_routes.module_for('documents') is None:
            self.assertTrue(all(x['status'] == 'unavailable' for x in documents))
            self.assertEqual(self.http('/api/product/document-upload', {})[0], 404)
        self.assertEqual(self.http('/api/product/document-upload', {}, token=False)[0], 401)

    def test_larger_upload_requires_explicit_owner_transport_and_keeps_other_limits(self):
        path = '/api/product/document-upload'
        body = dict(filename='fictional.txt', content_type='text/plain',
                    content_base64=base64.b64encode(b'x' * 131072).decode(), idempotency_key='fixture')
        self.assertEqual(self.http('/api/intake', body)[0], 413)
        module = SimpleNamespace(OPERATIONS={('POST', path)},
            upload_request_limit=lambda: 4 * ((131072 + 2) // 3) + 4096,
            dispatch=lambda app, owner, method, route, request: {'stub_transport_only': True})
        original = product_routes.module_for
        with patch.object(product_routes, 'module_for', side_effect=lambda name: module if name == 'documents' else original(name)):
            self.assertEqual(self.http(path, body), (200, {'stub_transport_only': True}))
            self.assertEqual(self.http(path, body, token=False)[0], 401)
            self.assertEqual(self.http('/api/intake', body)[0], 413)
            self.assertEqual(self.http(path, dict(body, content_base64='x' * 200000))[0], 413)

    def test_invalid_owner_limit_is_bounded_and_sanitized(self):
        for bad in (True, 0, product_routes.MAX_UPLOAD_BODY_LIMIT + 1):
            with self.subTest(limit=bad), patch.object(product_routes, 'module_for',
                    return_value=SimpleNamespace(upload_request_limit=lambda: bad)):
                code, result = self.http('/api/product/document-upload', {})
                self.assertEqual(code, 500)
                self.assertEqual(result['code'], 'document_transport_configuration_invalid')
                self.assertEqual(set(result), {'code', 'request_id'})


if __name__ == '__main__':
    unittest.main()
