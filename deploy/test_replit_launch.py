"""Provider-only evidence tests; no real credentials or provider calls."""
import json
import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from deploy import replit_launch


class ReplitLaunchTests(unittest.TestCase):
    def test_non_ascii_is_reported_without_modifying_environment(self):
        fixture = "fixture-\u2026"
        with patch.dict(os.environ, {"CLERK_SECRET_KEY": fixture}, clear=True):
            with patch.object(replit_launch, "check") as check:
                result = replit_launch.credential_evidence()
            self.assertFalse(result["key_ASCII"])
            self.assertFalse(result["authenticated_instance_match"])
            self.assertEqual(result["code"], "workflow_clerk_secret_non_ascii")
            self.assertEqual(os.environ["CLERK_SECRET_KEY"], fixture)
            self.assertNotIn(fixture, json.dumps(result))
            check.assert_not_called()

    def test_ascii_and_authenticated_match_are_separate_checks(self):
        with patch.dict(os.environ, {"CLERK_SECRET_KEY": "synthetic-test-only"}, clear=True):
            with patch.object(replit_launch, "prepare_auth"), patch.object(
                replit_launch, "check",
                return_value={"server_key_matches_public_signing_key": True},
            ):
                result = replit_launch.credential_evidence()
            self.assertTrue(result["key_ASCII"])
            self.assertTrue(result["authenticated_instance_match"])

    def test_exception_details_cannot_disclose_secret(self):
        fixture = "synthetic-sensitive-sentinel"
        with patch.dict(os.environ, {"CLERK_SECRET_KEY": fixture}, clear=True):
            with patch.object(replit_launch, "prepare_auth"), patch.object(
                replit_launch, "check", side_effect=RuntimeError(fixture),
            ):
                result = replit_launch.credential_evidence()
            self.assertEqual(result["code"], "workflow_auth_check_failed")
            self.assertNotIn(fixture, json.dumps(result))

    def test_existing_runtime_is_entered_in_same_process_after_diagnostic(self):
        output = StringIO()
        with patch.object(replit_launch, "credential_evidence", return_value={"safe": True}):
            with patch.object(replit_launch, "runtime_main") as runtime:
                with redirect_stdout(output):
                    replit_launch.main()
        runtime.assert_called_once_with()
        self.assertEqual(json.loads(output.getvalue()), {"safe": True})

    def test_runtime_failure_preserves_sanitized_error_boundary(self):
        output = StringIO()
        with patch.object(replit_launch, "credential_evidence", return_value={"safe": True}):
            with patch.object(
                replit_launch, "runtime_main", side_effect=RuntimeError("synthetic-private-detail")
            ):
                with redirect_stdout(output), self.assertRaises(SystemExit):
                    replit_launch.main()
        self.assertNotIn("synthetic-private-detail", output.getvalue())
        self.assertIn("Minder_Replit_startup_or_worker_failed_check_private_configuration", output.getvalue())


if __name__ == "__main__":
    unittest.main()
