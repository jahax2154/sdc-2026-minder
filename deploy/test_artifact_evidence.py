"""Published-artifact diagnostics identify omission without disclosing content."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from deploy.artifacts import SOURCE_IDS, runtime_evidence


class ArtifactEvidenceTests(unittest.TestCase):
    def test_distinguishes_missing_mismatch_and_verified_without_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "ml/minder_ml_starter"
            base.mkdir(parents=True)
            sources = []
            for index, source_id in enumerate(sorted(SOURCE_IDS)):
                relative = "raw/" + source_id + ".csv"
                payload = b"synthetic-payload-do-not-log"
                sources.append(dict(id=source_id, relative_path=relative,
                    license="CC BY 4.0", documented_version="31.0",
                    sha256=hashlib.sha256(payload).hexdigest()))
                path = base / relative
                path.parent.mkdir(exist_ok=True)
                if index != 0:
                    path.write_bytes(b"wrong-bytes" if index == 1 else payload)
            (base / "sources_manifest.json").write_text(json.dumps(dict(sources=sources)))
            evidence = runtime_evidence(root=root)
            self.assertNotIn("synthetic-payload", json.dumps(evidence))
            first, second, *verified = evidence["sources"]
            self.assertFalse(first["regular_file"])
            self.assertTrue(second["readable"])
            self.assertFalse(second["sha256_matches"])
            self.assertTrue(all(item["sha256_matches"] for item in verified))
            (base / sources[0]["relative_path"]).symlink_to(base / sources[2]["relative_path"])
            unsafe = runtime_evidence(root=root)["sources"][0]
            self.assertFalse(unsafe["safe_path"])
            self.assertFalse(unsafe["regular_file"])


if __name__ == "__main__":
    unittest.main()
