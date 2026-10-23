import os
from pathlib import Path
import tempfile
import unittest
from minder_app.document_storage import LocalDocumentStorage
from minder_app.store import AppError


class DocumentStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "private"
        self.storage = LocalDocumentStorage(self.root)
        self.key = "a" * 32

    def tearDown(self):
        self.tmp.cleanup()

    def test_private_restart_retry_and_delete(self):
        self.storage.put(self.key, b"Fictional document")
        self.storage.put(self.key, b"Fictional document")
        self.assertEqual(os.stat(self.root).st_mode & 0o777, 0o700)
        self.assertEqual(os.stat(self.root / self.key).st_mode & 0o777, 0o600)
        self.assertEqual(LocalDocumentStorage(self.root).get(self.key, 30), b"Fictional document")
        with self.assertRaises(AppError):
            self.storage.put(self.key, b"Changed document")
        self.storage.delete(self.key)
        self.storage.delete(self.key)
        self.assertFalse((self.root / self.key).exists())

    def test_bounded_read_traversal_and_symlink_denial(self):
        self.storage.put(self.key, b"Too large")
        with self.assertRaises(AppError):
            self.storage.get(self.key, 2)
        with self.assertRaises(AppError):
            self.storage.get("../../private", 200)
        external = Path(self.tmp.name) / "outside"
        external.write_bytes(b"Do not read or overwrite")
        key = "b" * 32
        (self.root / key).symlink_to(external)
        with self.assertRaises(AppError):
            self.storage.get(key, 100)
        with self.assertRaises(AppError):
            self.storage.put(key, b"Do not overwrite")
        self.storage.delete(key)
        self.assertEqual(external.read_bytes(), b"Do not read or overwrite")

    def test_unsafe_root_and_missing_file_are_sanitized(self):
        self.root.chmod(0o755)
        with self.assertRaises(AppError) as error:
            LocalDocumentStorage(self.root)
        self.assertEqual(error.exception.code, "document_storage_unavailable")
        self.root.chmod(0o700)
        with self.assertRaises(AppError) as error:
            self.storage.get(self.key, 100)
        self.assertEqual(error.exception.code, "document_storage_read_failed")
