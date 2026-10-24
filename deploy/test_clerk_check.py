import base64
from types import SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock
from deploy.clerk_check import check
from deploy.operator import OperatorError


class ClerkPreflightTests(unittest.TestCase):
    def test_backend_instance_must_match_public_key_without_claiming_login(self):
        from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        public = generate_private_key(public_exponent=65537, key_size=2048).public_key()
        numbers = public.public_numbers()
        def encoded(number):
            return base64.urlsafe_b64encode(number.to_bytes((number.bit_length()+7)//8, "big")).decode().rstrip("=")
        values = dict(MINDER_CLERK_INSTANCE_MODE="preview", CLERK_PUBLISHABLE_KEY="pk_test_example",
            CLERK_SECRET_KEY="sk_test_private_placeholder", CLERK_JWT_KEY=public.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode())
        discovery = patch("deploy.clerk_check.derive_clerk_public", return_value={"CLERK_JWT_KEY": values["CLERK_JWT_KEY"]})
        discovery.start()
        self.addCleanup(discovery.stop)
        client = MagicMock()
        client.jwks.get_jwks.return_value = SimpleNamespace(keys=[SimpleNamespace(kty="RSA", n=encoded(numbers.n), e=encoded(numbers.e))])
        with patch("clerk_backend_api.Clerk", return_value=client):
            result = check(values)
        self.assertTrue(result["server_key_matches_public_signing_key"])
        self.assertFalse(result["live_login"])
        self.assertFalse(result["two_account_isolation"])
        self.assertNotIn(values["CLERK_SECRET_KEY"], str(result))
        client.jwks.get_jwks.assert_called_once_with(timeout_ms=5000, retries=None)
        client.jwks.get_jwks.return_value = SimpleNamespace(keys=[])
        with patch("clerk_backend_api.Clerk", return_value=client), self.assertRaises(OperatorError):
            check(values)
        client.jwks.get_jwks.side_effect = RuntimeError(values["CLERK_SECRET_KEY"])
        with patch("clerk_backend_api.Clerk", return_value=client), self.assertRaises(OperatorError) as caught:
            check(values)
        self.assertNotIn(values["CLERK_SECRET_KEY"], str(caught.exception))
        with self.assertRaises(OperatorError):
            check(dict(values, CLERK_SECRET_KEY="sk_live_wrong_realm"))


if __name__ == "__main__":
    unittest.main()
