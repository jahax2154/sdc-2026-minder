import io
import json
import unittest
from urllib.error import HTTPError, URLError
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError


class Reply(io.BytesIO):
    headers = {"x-request-id": "upstream-test"}


class GroqTests(unittest.TestCase):
    def test_missing_access_is_honest(self):
        self.assertEqual(GroqAdapter(key="").probe()["code"], "provider_credentials_missing")

    def test_mock_discovery_and_call(self):
        requests = []
        def opener(req, timeout):
            requests.append(req)
            data = {"data": [{"id": "mock-model"}]} if req.data is None else {
                "choices": [{"message": {"content": "OK"}}], "usage": {"total_tokens": 3}}
            return Reply(json.dumps(data).encode())
        result = GroqAdapter(key="test-only", model="mock-model", opener=opener).probe()
        self.assertEqual(result["status"], "available")
        self.assertEqual(len(requests), 2)
        self.assertEqual(json.loads(requests[1].data)["max_completion_tokens"], 8)

    def test_bounded_retry_and_redacted_error(self):
        calls = []
        def fail(req, timeout):
            calls.append(1)
            raise HTTPError(req.full_url, 429, "SECRET", {}, io.BytesIO(b"secret"))
        with self.assertRaises(ProviderError) as ctx:
            GroqAdapter(key="secret", model="mock", opener=fail, retries=2,
                        sleep=lambda _: None).complete([])
        self.assertEqual(len(calls), 3)
        self.assertNotIn("secret", str(ctx.exception))
        self.assertEqual(ctx.exception.code, "provider_rate_limited")

    def test_auth_not_retried_and_network_is_structured(self):
        for status, expected in [(401, "provider_auth_failed"), (403, "provider_access_denied")]:
            def fail(req, timeout):
                raise HTTPError(req.full_url, status, "secret", {}, io.BytesIO(b"secret"))
            self.assertEqual(GroqAdapter(key="x", opener=fail).probe()["code"], expected)
        def offline(*args, **kwargs):
            raise URLError("private host")
        self.assertEqual(GroqAdapter(key="x", opener=offline, retries=0).probe()["code"],
                         "provider_network_or_timeout")

    def test_malformed_response(self):
        with self.assertRaises(ProviderError):
            GroqAdapter(key="x", model="mock", opener=lambda *a, **k: Reply(b"{}")).complete([])
