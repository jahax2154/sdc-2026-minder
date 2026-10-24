from pathlib import Path
import tempfile
import unittest
from minder_app.config import ProviderConfig
from minder_app.provider_access import verify, selected_model


class MockProvider:
    model = ""
    def models(self):
        return ["llama-3.1-8b-instant"]
    def complete(self, messages, **kwargs):
        return {"status": "available", "text": "mock-only"}
    def complete_tool(self, messages, tool, **kwargs):
        return {"status": "available", "text": '{"ready":true}', "tool_call": {"arguments_validated": True}}


class AccessTests(unittest.TestCase):
    def test_mock_discovery_verified_selection_without_secret_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "model.json"
            result = verify(ProviderConfig(api_key="mock-private-only"), provider=MockProvider(), path=target)
            self.assertTrue(all(result.values()))
            self.assertNotIn("mock-private", target.read_text())
            self.assertEqual(selected_model(target), "llama-3.1-8b-instant")
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertTrue(all(type(v) is bool for v in result.values()))

    def test_no_selection_when_tool_verification_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "model.json"
            provider = MockProvider()
            provider.complete_tool = lambda *a, **k: {"status":"unavailable"}
            result = verify(ProviderConfig(api_key="mock-only"), provider=provider, path=target)
            self.assertFalse(result["tool_request_success"])
            self.assertFalse(target.exists())
