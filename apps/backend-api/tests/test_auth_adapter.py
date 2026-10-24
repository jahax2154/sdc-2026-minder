"""Real official SDK and generated RSA test tokens; no live Clerk account claimed."""
import importlib.util
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from minder_app.auth_adapter import AuthConfig, ClerkIdentityVerifier, public_config
from minder_app.store import AppError


class ConfigTests(unittest.TestCase):
    def test_no_implicit_anonymous_fallback_or_secret_in_public_config(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(public_config()["status"], "unavailable")
            with self.assertRaises(AppError) as caught:
                AuthConfig.from_env()
            self.assertEqual(caught.exception.status, 503)


@unittest.skipUnless(importlib.util.find_spec("clerk_backend_api"), "official Clerk SDK requires the isolated Python3.12 test environment")
class ClerkVerificationTests(unittest.TestCase):
    def setUp(self):
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = self.key.public_key().public_bytes(serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.config = AuthConfig("https://test.clerk.accounts.dev", ("https://minder.example",),
                                 "pk_test_example", "sk_test_example", public, "minder-test")
        self.verifier = ClerkIdentityVerifier(self.config)
        self.sessions = Mock()
        self.verifier.client = SimpleNamespace(sessions=self.sessions)

    def token(self, **changes):
        import jwt
        claims = dict(iss=self.config.issuer, sub="user_alice", sid="sess_alice", v=2,
                      azp="https://minder.example", aud="minder-test", exp=int(time.time()) + 60,
                      nbf=int(time.time()) - 5, iat=int(time.time()) - 5)
        claims.update(changes)
        return jwt.encode(claims, self.key, algorithm="RS256")

    def session(self, user="alice", status="active"):
        self.sessions.get.return_value = SimpleNamespace(id="sess_" + user, user_id="user_" + user, status=status)

    def assert_denied(self, token):
        with self.assertRaises(AppError) as caught:
            self.verifier.verify_identity(token)
        self.assertEqual(caught.exception.status, 401)

    def test_two_verified_accounts_remain_distinct_and_identity_immutable(self):
        self.session()
        alice = self.verifier.verify_identity(self.token())
        self.session("bob")
        bob = self.verifier.verify_identity(self.token(sub="user_bob", sid="sess_bob"))
        self.assertNotEqual(dict(alice)["subject"], dict(bob)["subject"])
        self.assertEqual(alice.issuer, bob.issuer)
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            alice.subject = "user_bob"
        self.assertNotIn("token", dict(alice))

    def test_expiry_signature_issuer_origin_audience_and_identity_tampering(self):
        self.session()
        for changes in ({"exp": int(time.time()) - 1}, {"iss": "https://evil.example"},
                        {"azp": "https://evil.example"}, {"aud": "another-app"}, {"sid": None}):
            self.assert_denied(self.token(**changes))
        token = self.token()
        head, payload, signature = token.split(".")
        self.assert_denied(head + "." + payload + "." + ("A" if signature[0] != "A" else "B") + signature[1:])
        self.assert_denied("user_alice")
        self.assert_denied("")
        self.sessions.get.assert_not_called()

    def test_logout_invalidates_still_unexpired_token_and_mismatch_rejected(self):
        token = self.token()
        self.session()
        self.assertEqual(self.verifier.verify_identity(token).subject, "user_alice")
        self.session(status="revoked")
        self.assert_denied(token)
        self.session("bob")
        self.assert_denied(token)

    def test_provider_outage_fails_closed_and_public_config_is_allowlisted(self):
        self.sessions.get.side_effect = TimeoutError("private provider detail")
        with self.assertRaises(AppError) as caught:
            self.verifier.verify_identity(self.token())
        self.assertEqual(caught.exception.status, 503)
        self.assertNotIn("private", str(caught.exception))
        env = dict(MINDER_AUTH_PROVIDER="clerk", CLERK_ISSUER=self.config.issuer,
                   CLERK_AUTHORIZED_PARTIES="https://minder.example", CLERK_PUBLISHABLE_KEY="pk_test_example",
                   CLERK_SECRET_KEY="sk_test_hidden", CLERK_JWT_KEY=self.config.jwt_key)
        with patch.dict("os.environ", env, clear=True):
            result = public_config()
            self.assertEqual(result["status"], "configured")
            self.assertNotIn("sk_test_hidden", str(result))
            self.assertNotIn(self.config.jwt_key, str(result))

    def test_sdk_identity_drives_actual_wsgi_owner_isolation_expiry_and_logout(self):
        import tempfile
        from pathlib import Path
        from minder_app.api import Application
        from minder_app.store import Store
        from minder_ml.intelligence.integration_cli import wsgi_request
        def session_lookup(*, session_id, **kwargs):
            name = session_id[5:]
            return SimpleNamespace(id=session_id, user_id="user_" + name, status="active")
        self.sessions.get.side_effect = session_lookup
        env = dict(MINDER_ENV="production", MINDER_AUTH_PROVIDER="clerk", CLERK_ISSUER=self.config.issuer,
                   CLERK_AUTHORIZED_PARTIES="https://minder.example", CLERK_PUBLISHABLE_KEY="pk_test_example",
                   CLERK_SECRET_KEY="sk_test_hidden", CLERK_JWT_KEY=self.config.jwt_key, CLERK_AUDIENCE="minder-test")
        with tempfile.TemporaryDirectory() as directory, patch.dict("os.environ", env, clear=True), \
                patch("minder_app.auth_adapter._verifier", return_value=self.verifier):
            app = Application(Store(Path(directory) / "test.sqlite3"))
            alice = self.token()
            bob = self.token(sub="user_bob", sid="sess_bob")
            def request(method, path, body=None, token=alice):
                return wsgi_request(app, method, path, body, token)
            self.assertEqual(request("POST", "/api/session", {})[0], 401)
            code, profile = request("PUT", "/api/profile", {"profile": {"synthetic": True}})
            self.assertEqual(code, 200)
            self.assertEqual(request("GET", "/api/profile", token=bob)[0], 404)
            code, conversation = request("GET", "/api/product/mindbot-conversation")
            self.assertEqual(code, 200)
            conversation_id = conversation["conversation"]["conversation_id"]
            self.assertEqual(request("GET", "/api/product/conversation", {"conversation_id": conversation_id}, bob)[0], 404)
            # New Application/Store still maps the same provider pair to the same owner.
            app = Application(Store(Path(directory) / "test.sqlite3"))
            self.assertEqual(request("GET", "/api/profile")[1]["profile_id"], profile["profile_id"])
            self.assertEqual(request("GET", "/api/profile", token=self.token(exp=int(time.time()) - 1))[0], 401)
            self.sessions.get.side_effect = None
            self.session(status="revoked")
            self.assertEqual(request("GET", "/api/profile")[0], 401)
