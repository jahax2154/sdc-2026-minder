import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from deploy.operator import (OperatorError, approved_release, confirmed_budget, doctor,
                             private_config, service_variables, verify_target, verify_volume,
                             derive_clerk_public, save_derived_public)


class OperatorTests(unittest.TestCase):
    def test_selected_replit_target_never_requires_or_calls_Railway(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from deploy.operator import main
        report = doctor({"MINDER_HOSTING_TARGET": "replit"})
        self.assertEqual(report["hosting_target"], "replit")
        self.assertFalse(any(name.startswith("RAILWAY_") for name in report["missing_local_fields"]))
        for operation in ("inspect", "prepare-service", "deploy"):
            output = StringIO()
            with patch("sys.argv", ["operator", operation]), patch("deploy.operator.private_config",
                    return_value={"MINDER_HOSTING_TARGET": "replit"}), patch("deploy.operator.railway") as provider, \
                    redirect_stdout(output), self.assertRaises(SystemExit):
                main()
            self.assertEqual(json.loads(output.getvalue())["code"], "Railway_actions_disabled_for_selected_Replit_target")
            provider.assert_not_called()

    def test_preview_discovery_needs_no_secret_and_preserves_existing_file_values(self):
        import base64
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        public = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
        numbers = public.public_numbers()
        def encoded(number):
            return base64.urlsafe_b64encode(number.to_bytes((number.bit_length()+7)//8, "big")).decode().rstrip("=")
        jwk = dict(kty="RSA", alg="RS256", use="sig", n=encoded(numbers.n), e=encoded(numbers.e))
        values = dict(MINDER_CLERK_INSTANCE_MODE="preview", MINDER_JUDGE_URL="https://judge.up.railway.app",
            CLERK_PUBLISHABLE_KEY="pk_test_"+base64.b64encode(b"minder.clerk.accounts.dev$").decode())
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"keys": [jwk]}).encode()
        opener = MagicMock()
        opener.open.return_value = response
        with patch("deploy.operator.build_opener", return_value=opener):
            updates = derive_clerk_public(values)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://minder.clerk.accounts.dev/.well-known/jwks.json")
        self.assertIsNone(request.get_header("Authorization"))
        self.assertEqual(updates["CLERK_JWT_KEY"], public.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode())
        self.assertEqual(updates["CLERK_ISSUER"], "https://minder.clerk.accounts.dev")
        self.assertEqual(updates["CLERK_AUTHORIZED_PARTIES"], values["MINDER_JUDGE_URL"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"config"
            text = "# Preserve this comment\nRAILWAY_TOKEN=do-not-change\nCLERK_ISSUER=\nCLERK_JWT_KEY=\n"
            path.write_text(text)
            path.chmod(0o600)
            original = private_config(path)
            save_derived_public(path, original, updates)
            saved = private_config(path)
            self.assertEqual(saved["RAILWAY_TOKEN"], original["RAILWAY_TOKEN"])
            self.assertEqual(saved["CLERK_JWT_KEY"], updates["CLERK_JWT_KEY"])
            self.assertTrue(path.read_text().startswith("# Preserve this comment\n"))
            with self.assertRaises(OperatorError):
                save_derived_public(path, original, updates)
        with patch("deploy.operator.build_opener") as network:
            self.assertEqual(derive_clerk_public(dict(values, **updates)), {})
            for host in ("localhost", "127.0.0.1", "evil.example", "minder.clerk.accounts.dev/other"):
                bad = "pk_test_" + base64.b64encode((host+"$").encode()).decode()
                with self.assertRaises(OperatorError):
                    derive_clerk_public(dict(values, CLERK_PUBLISHABLE_KEY=bad))
            network.assert_not_called()
        response.__enter__.return_value.read.return_value = json.dumps({"keys": [jwk, jwk]}).encode()
        with patch("deploy.operator.build_opener", return_value=opener), self.assertRaises(OperatorError):
            derive_clerk_public(values)

    def test_private_configuration_redaction_permissions_and_no_bypass_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.deploy.local"
            path.write_text('RAILWAY_TOKEN=private-token\nCLERK_SECRET_KEY=private-key\nCLERK_JWT_KEY="line1\\nline2"\n')
            path.chmod(0o600)
            values = private_config(path)
            self.assertEqual(values["CLERK_JWT_KEY"], "line1\nline2")
            self.assertNotIn("private-token", json.dumps(doctor(values)))
            self.assertNotIn("private-key", json.dumps(doctor(values)))
            path.chmod(0o644)
            with self.assertRaises(OperatorError):
                private_config(path)
            path.chmod(0o600)
            link = Path(directory) / "linked"
            link.symlink_to(path)
            with self.assertRaises(OperatorError):
                private_config(link)
            path.write_text("MINDER_TEST_AUTH_BYPASS=1\n")
            with self.assertRaises(OperatorError):
                private_config(path)

    def test_no_provider_target_or_budget_inference(self):
        for value in ("", "0", "-1", "nan", "inf"):
            with self.assertRaises(OperatorError):
                confirmed_budget({"MINDER_DEPLOY_MAX_USD": value})
        values = dict(RAILWAY_PROJECT_ID="selected-project", RAILWAY_ENVIRONMENT_ID="selected-env",
                      RAILWAY_SERVICE_ID="selected-service")
        with patch("deploy.operator.railway", return_value={"projectToken": {"projectId": "other", "environmentId": "selected-env"}}):
            with self.assertRaises(OperatorError):
                verify_target(values)
        with self.assertRaises(OperatorError):
            approved_release(Path("/private/tmp/nonexistent-minder-release-approval.json"))

    def test_volume_must_match_service_environment_and_data_mount(self):
        values = dict(RAILWAY_PROJECT_ID="project", RAILWAY_ENVIRONMENT_ID="env", RAILWAY_SERVICE_ID="service")
        schema = {"__type": {"fields": [{"name": key} for key in ("mountPath", "serviceId", "environmentId")]}}
        for mount, service in (("/tmp", "service"), ("/data", "another")):
            data = {"project": {"volumes": {"edges": [{"node": {"volumeInstances": {"edges": [{"node":
                dict(mountPath=mount, serviceId=service, environmentId="env")} ]}}}]}}}
            with patch("deploy.operator.railway", side_effect=[schema, data]):
                with self.assertRaises(OperatorError):
                    verify_volume(values)

    def test_only_runtime_fields_are_sent_to_the_provider(self):
        import base64
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        public = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
        publishable = "pk_live_" + base64.b64encode(b"clerk.judge.example$").decode()
        values = dict(MINDER_CLERK_INSTANCE_MODE="production", CLERK_PUBLISHABLE_KEY=publishable, CLERK_SECRET_KEY="sk_live_placeholder",
            CLERK_JWT_KEY=public, CLERK_ISSUER="https://clerk.judge.example",
            CLERK_AUTHORIZED_PARTIES="https://judge.example", MINDER_JUDGE_URL="https://judge.example",
            GROQ_API_KEY="private-groq", MINDER_LLM_DAILY_LIMIT="20", RAILWAY_TOKEN="private-provider-token",
            CLERK_ACCEPTANCE_USER_A="user_a", CLERK_ACCEPTANCE_USER_B="user_b")
        result = service_variables(values, "a" * 40)
        self.assertNotIn("RAILWAY_TOKEN", result)
        self.assertNotIn("CLERK_ACCEPTANCE_USER_A", result)
        self.assertEqual(result["MINDER_ENV"], "production")
        self.assertEqual(result["MINDER_RELEASE_SHA"], "a" * 40)
        self.assertEqual(result["MINDER_DOCUMENT_STORAGE"], "private-volume")
        local_public = {key: value for key, value in values.items() if key not in ("CLERK_SECRET_KEY", "GROQ_API_KEY")}
        preserved = service_variables(local_public, "a" * 40, {"CLERK_SECRET_KEY": None, "GROQ_API_KEY": None})
        self.assertNotIn("CLERK_SECRET_KEY", preserved)
        self.assertNotIn("GROQ_API_KEY", preserved)
        with self.assertRaises(OperatorError):
            service_variables(dict(values, MINDER_JUDGE_URL="http://127.0.0.1"), "a" * 40)
        with self.assertRaises(OperatorError):
            service_variables(dict(values, CLERK_ISSUER="https://another-instance.example"), "a" * 40)
        with self.assertRaises(OperatorError):
            service_variables(dict(values, CLERK_PUBLISHABLE_KEY=publishable.replace("pk_live_", "pk_test_"),
                                   CLERK_SECRET_KEY="sk_test_placeholder"), "a" * 40)
        preview = dict(values, MINDER_CLERK_INSTANCE_MODE="preview",
                       CLERK_PUBLISHABLE_KEY=publishable.replace("pk_live_", "pk_test_"),
                       CLERK_SECRET_KEY="sk_test_placeholder")
        preview_result = service_variables(preview, "a" * 40)
        self.assertEqual(preview_result["MINDER_ENV"], "production")
        self.assertEqual(preview_result["MINDER_AUTH_MODE"], "managed")
        self.assertNotIn("MINDER_CLERK_INSTANCE_MODE", preview_result)
        with self.assertRaises(OperatorError):
            service_variables(dict(values, MINDER_CLERK_INSTANCE_MODE="preview"), "a" * 40)
        with self.assertRaises(OperatorError):
            service_variables(dict(values, MINDER_CLERK_INSTANCE_MODE=""), "a" * 40)

    def test_live_public_probe_cannot_claim_private_acceptance_and_rejects_bypass(self):
        from deploy.live_probe import check
        values = dict(MINDER_JUDGE_URL="https://judge.example", CLERK_AUTHORIZED_PARTIES="https://judge.example")
        health = (200, {"runtime_revision": "a" * 40})
        config = (200, dict(mode="managed", anonymous_session_allowed=False, provider="clerk", status="configured"))
        with patch("deploy.live_probe.request", side_effect=[health, config] + [(401, {})] * 8):
            result = check(values, "a" * 40)
        self.assertFalse(result["live_login"])
        self.assertFalse(result["hosted_daily_event"])
        with patch("deploy.live_probe.request", side_effect=[health, config] + [(401, {})] * 7 + [(200, {"token": "bad"})]):
            with self.assertRaises(OperatorError):
                check(values, "a" * 40)


if __name__ == "__main__":
    unittest.main()
