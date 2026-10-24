"""Generated library artifact integrity and safe ownership boundaries."""
import json
from pathlib import Path
import tempfile
import subprocess
import unittest

from deploy.replit_bundle import package, MANIFEST
from deploy.replit_bootstrap import verify, StartupFailure, DEPENDENCY_DIRECTORY


class BundleTests(unittest.TestCase):
    def test_copy_keeps_library_data_and_rebuilds_only_owned_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "build-site"
            source.mkdir()
            (source / "module.py").write_text("value = 1\n")
            (source / "license.pem").write_text("synthetic build data\n")
            (source / "_virtualenv.pth").write_text("not exported\n")
            lock = root / "uv.lock"
            lock.write_text("synthetic frozen lock\n")
            destination = root / "runtime"
            package(source, destination, lock)
            self.assertTrue((destination / "module.py").is_file())
            self.assertTrue((destination / "license.pem").is_file())
            self.assertFalse((destination / "_virtualenv.pth").exists())
            self.assertFalse((destination / "bin/python").exists())
            (root / ".gitignore").write_text("*.pem\n*.pth\n.pythonlibs/\n")
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            ignored = subprocess.run(["git", "check-ignore", "--quiet", "runtime/license.pem"], cwd=root)
            self.assertEqual(ignored.returncode, 1, "public dependency data must not inherit source-secret ignore rules")
            (destination / "obsolete.py").write_text("old\n")
            package(source, destination, lock)
            self.assertFalse((destination / "obsolete.py").exists())

    def test_unknown_destination_is_never_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, destination = root / "source", root / "destination"
            source.mkdir()
            destination.mkdir()
            retained = destination / "user-file"
            retained.write_text("preserve\n")
            with self.assertRaisesRegex(ValueError, "destination_not_owned"):
                package(source, destination, root / "unused-lock")
            self.assertEqual(retained.read_text(), "preserve\n")

    def test_runtime_rejects_bundle_from_different_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / DEPENDENCY_DIRECTORY
            site.mkdir(parents=True)
            (root / "uv.lock").write_text("new lock\n")
            (site / MANIFEST).write_text(json.dumps(dict(format="minder-locked-python-libraries-v1", lock_sha256="old")))
            with self.assertRaisesRegex(StartupFailure, "bundle_manifest_invalid"):
                verify(root)


if __name__ == "__main__":
    unittest.main()
