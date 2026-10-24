"""Bounded configuration/packaging tests; no hosted-account or mount claims."""
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from deploy.artifacts import inventory, pack, checked_url
from deploy.runtime import settings


class CandidateTests(unittest.TestCase):
    def test_sources_exact_hashes_and_pack_contains_only_licensed_runtime_csvs(self):
        data = inventory(verify=True)
        self.assertEqual(len(data["sources"]), 4)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "runtime.tar.gz"
            self.assertEqual(pack(output)["source_count"], 4)
            with tarfile.open(output) as archive:
                names = archive.getnames()
            self.assertEqual(len(names), 5)
            self.assertFalse(any("galaxy" in name or "sqlite" in name or ".env" in name for name in names))

    def test_fetch_target_and_redirects_are_bounded(self):
        for uri in ("http://www.onetcenter.org/file", "https://127.0.0.1/file",
                    "https://user:pass@www.onetcenter.org/file", "https://evil.example/file"):
            with self.assertRaises(ValueError):
                checked_url(uri)

    def test_config_fails_closed_without_mount_auth_and_provider(self):
        with self.assertRaises(ValueError):
            settings({})
        env = dict(RAILWAY_VOLUME_MOUNT_PATH="/data", MINDER_DB_PATH="/data/minder/runtime.sqlite3",
                   MINDER_DATA_ROOT="/data", MINDER_ENV="production",
                   MINDER_AUTH_MODE="managed", MINDER_AUTH_PROVIDER="clerk", PORT="8080",
                   GROQ_MODEL="qwen/qwen3.8-27b", GROQ_API_KEY="test-only")
        with patch.object(Path, "is_mount", return_value=True):
            self.assertEqual(settings(env)[1], 8080)
            with self.assertRaises(ValueError):
                settings(dict(env, MINDER_DB_PATH="/tmp/runtime.sqlite3"))
            with self.assertRaises(ValueError):
                settings(dict(env, MINDER_AUTH_MODE="anonymous"))
        with patch.object(Path, "is_mount", return_value=False):
            with self.assertRaises(ValueError):
                settings(env)

    def test_manifest_is_one_service_one_volume_candidate(self):
        manifest = json.loads((Path(__file__).parent / "railway.json").read_text())
        self.assertEqual(manifest["deploy"]["numReplicas"], 1)
        self.assertNotIn("cronSchedule", manifest["deploy"])


if __name__ == "__main__":
    unittest.main()
