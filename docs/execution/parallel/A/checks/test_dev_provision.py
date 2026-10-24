"""Provisioning acceptance in disposable A artifacts; original inputs read-only."""
import json
from pathlib import Path
import tempfile
import unittest
from provision_dev_inputs import ROOT, digest, provision


class ProvisionTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / 'ml/artifacts/session-a/provision-checks'
        base.mkdir(parents=True, exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(dir=base)
        self.work = Path(self.folder.name)
        self.source = ROOT / 'ml/minder_ml_starter'
        self.entries = json.loads((ROOT / 'docs/execution/parallel/source_snapshot.v1.json').read_text())['source_files']

    def tearDown(self):
        self.folder.cleanup()

    def test_exact_pack_copies_read_only_then_preserves_inodes_and_rejects_overwrite(self):
        destination = self.work / 'copy'
        result = provision(source_root=self.source, destination_root=destination)
        self.assertEqual(result['copied'], 13)
        inodes = [(destination/e['path']).stat().st_ino for e in self.entries]
        self.assertEqual(provision(source_root=self.source, destination_root=destination)['copied'], 0)
        self.assertEqual(inodes, [(destination/e['path']).stat().st_ino for e in self.entries])
        self.assertEqual(len([p for p in destination.rglob('*') if p.is_file()]), 13)
        target = destination / self.entries[0]['path']
        target.chmod(0o644)
        target.write_bytes(b'fictional mismatched source fixture')
        target.chmod(0o444)
        before = digest(target)
        with self.assertRaisesRegex(ValueError, 'existing_destination_hash_mismatch_no_overwrite'):
            provision(source_root=self.source, destination_root=destination)
        self.assertEqual(digest(target), before)
        for entry in self.entries:
            original = self.source / entry['path']
            self.assertEqual(digest(original), entry['sha256'])
            self.assertFalse(original.stat().st_mode & 0o222)

    def test_missing_or_external_pack_refused_before_writing(self):
        destination = self.work / 'absent'
        with self.assertRaisesRegex(ValueError, 'source_missing_or_hash_mismatch'):
            provision(source_root=self.work/'missing-pack', destination_root=destination)
        self.assertFalse(destination.exists())
        with self.assertRaisesRegex(ValueError, 'destination_must_stay_in_current_worktree'):
            provision(source_root=self.source, destination_root=ROOT.parent/'session-b/forbidden-input-copy')
        self.assertFalse((ROOT.parent/'session-b/forbidden-input-copy').exists())


if __name__ == '__main__':
    unittest.main()
