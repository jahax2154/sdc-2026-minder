"""Runtime preflight failure boundaries and single-launcher handoff."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deploy import replit_bootstrap as boot


class BootstrapTests(unittest.TestCase):
    def test_wrong_module_version_fails_before_dependencies(self):
        with patch.object(boot.sys, "version_info", (3, 13, 0)):
            with self.assertRaisesRegex(boot.StartupFailure, "requires_3_12"):
                boot.verify()

    def test_missing_packaged_dependencies_have_precise_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(boot.StartupFailure, "built_dependency_directory_missing"):
                boot.verify(Path(directory))

    def test_import_exception_never_discloses_its_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / boot.DEPENDENCY_DIRECTORY).mkdir(parents=True)
            (root / "uv.lock").write_text('[[package]]\nname="pyjwt"\nversion="2.15.1"\n')
            with patch.object(boot.importlib, "import_module", side_effect=RuntimeError("private-sentinel")):
                with self.assertRaises(boot.StartupFailure) as error:
                    boot.verify(root, require_bundle=False)
            self.assertEqual(str(error.exception), "required_import_or_pin_failed:jwt")
            self.assertNotIn("private-sentinel", str(error.exception))

    def test_check_mode_never_enters_application(self):
        with patch.object(boot.sys, "argv", ["bootstrap", "--check"]), patch.object(
            boot, "verify", return_value={"checked": True}
        ), patch.object(boot.runpy, "run_module") as launch, redirect_stdout(StringIO()):
            boot.main()
            launch.assert_not_called()

    def test_verified_runtime_enters_existing_launcher_once(self):
        output = StringIO()
        with patch.object(boot.sys, "argv", ["bootstrap"]), patch.object(
            boot, "verify", return_value={"checked": True}
        ), patch.object(boot.runpy, "run_module") as launch, redirect_stdout(output):
            boot.main()
        launch.assert_called_once_with("deploy.replit_launch", run_name="__main__")
        lines = output.getvalue().splitlines()
        self.assertEqual(json.loads(lines[0])["event"], "minder_python_runtime_probe")
        self.assertEqual(json.loads(lines[1]), {"checked": True})


if __name__ == "__main__":
    unittest.main()
