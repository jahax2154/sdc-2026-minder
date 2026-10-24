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

    def test_volume_guard_has_no_environment_only_durability_bypass(self):
        from unittest.mock import patch
        from minder_app.store import Store
        from minder_app.document_storage import PrivateVolumeDocumentStorage
        from minder_app.documents import DocumentLibrary
        mount = Path(self.tmp.name).resolve()
        with self.assertRaises(AppError):
            Store.on_volume(mount)
        # Software mount fixture, explicitly not actual hosted-volume evidence.
        with patch("os.path.ismount", return_value=True):
            store = Store.on_volume(mount)
            self.assertEqual(store.engine, "sqlite")
            self.assertEqual(store.durability_status, "mount_verified_restart_pending")
            library = DocumentLibrary.from_environment(store, {"MINDER_DOCUMENT_STORAGE":"private-volume"})
            self.assertEqual(library.list("fictional-owner")["storage"]["mode"], "private-volume")
            self.assertFalse(library.list("fictional-owner")["storage"]["durable_hosting_verified"])
            storage = library.storage
            storage.put(self.key,b"Fictional CV")
        with self.assertRaises(AppError):
            store.connect()
        with self.assertRaises(AppError):
            storage.get(self.key,100)
        with patch("os.path.ismount", return_value=True):
            with self.assertRaises(AppError):
                PrivateVolumeDocumentStorage(mount, mount.parent/"outside-mount")
            with self.assertRaises(AppError):
                Store.on_volume(mount, mount.parent/"outside.sqlite3")
            storage.delete(self.key)

    def test_online_backup_preserves_versions_and_never_overwrites(self):
        from minder_app.store import Store
        store = Store(Path(self.tmp.name)/"source.sqlite3")
        saved = store.put("fictional-owner","profile","fictional-owner",{"education":"Fictional"},None)
        backup = Path(self.tmp.name)/"backups/snapshot.sqlite3"
        self.assertEqual(store.backup(backup)["status"],"created")
        self.assertEqual(backup.stat().st_mode & 0o777,0o600)
        restored = Store(backup)
        self.assertEqual(restored.get("fictional-owner","profile","fictional-owner"),saved)
        with self.assertRaises(AppError):
            store.backup(backup)
        self.assertEqual(restored.get("fictional-owner","profile","fictional-owner"),saved)
