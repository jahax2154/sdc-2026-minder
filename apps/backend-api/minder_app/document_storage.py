"""Private object storage boundary. Local implementation is development-only."""
from contextlib import contextmanager
import os
from pathlib import Path
import re
import stat
from typing import Protocol
from .store import AppError


class DocumentStorage(Protocol):
    def put(self, key: str, content: bytes) -> None:
        """Write immutable bytes; identical retries are safe, failures can retry."""

    def get(self, key: str, max_bytes: int) -> bytes:
        """Read bounded private bytes, or fail with a sanitized error."""

    def delete(self, key: str) -> None:
        """Idempotently remove bytes; return only when absent."""


class LocalDocumentStorage:
    """Opaque 0600 objects in a 0700 directory, never in a public static root."""
    mode = "local-development"
    durable_hosting_verified = False

    def __init__(self, root):
        self.root = Path(root)
        if not self.root.is_absolute():
            raise AppError("document_storage_absolute_path_required", 500)
        try:
            self.root.mkdir(parents=True, mode=0o700, exist_ok=True)
            with self.directory():
                pass
        except OSError:
            raise AppError("document_storage_unavailable", 500) from None

    @contextmanager
    def directory(self):
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(fd)
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
                raise OSError("unsafe directory")
            yield fd
        finally:
            os.close(fd)

    @staticmethod
    def check_key(key):
        if not isinstance(key, str) or not re.fullmatch(r"[a-f0-9]{32}", key):
            raise AppError("invalid_document_storage_key", 500)

    def put(self, key, content):
        self.check_key(key)
        try:
            with self.directory() as directory:
                try:
                    fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=directory)
                except FileExistsError:
                    if self.get(key, len(content)) != content:
                        raise AppError("document_storage_key_conflict", 500)
                    return
                try:
                    with os.fdopen(fd, "wb") as handle:
                        handle.write(content)
                        handle.flush()
                        os.fsync(handle.fileno())
                except BaseException:
                    os.unlink(key, dir_fd=directory)
                    raise
        except OSError:
            raise AppError("document_storage_write_failed", 500) from None

    def get(self, key, max_bytes):
        self.check_key(key)
        try:
            with self.directory() as directory:
                fd = os.open(key, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                with os.fdopen(fd, "rb") as handle:
                    info = os.fstat(handle.fileno())
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                            or stat.S_IMODE(info.st_mode) & 0o077 or info.st_size > max_bytes):
                        raise AppError("document_storage_integrity_failed", 500)
                    content = handle.read(max_bytes + 1)
                    if len(content) > max_bytes:
                        raise AppError("document_storage_integrity_failed", 500)
                    return content
        except OSError:
            raise AppError("document_storage_read_failed", 500) from None

    def delete(self, key):
        self.check_key(key)
        try:
            with self.directory() as directory:
                try:
                    os.unlink(key, dir_fd=directory)
                except FileNotFoundError:
                    pass
        except OSError:
            raise AppError("document_storage_delete_failed", 500) from None


class PrivateVolumeDocumentStorage(LocalDocumentStorage):
    """Same private byte adapter, guarded by an actual mounted volume each use.

    A successful mount check is not hosted restart/backup acceptance evidence.
    """
    mode = "private-volume"
    durability_status = "mount_verified_restart_pending"

    def __init__(self, mount_root, root):
        from .store import Store
        self.mount_root = Store.verify_volume(mount_root)
        if not Path(root).is_absolute() or not Path(root).resolve().is_relative_to(self.mount_root):
            raise AppError("document_storage_outside_verified_volume", 500)
        super().__init__(root)

    @contextmanager
    def directory(self):
        from .store import Store
        Store.verify_volume(self.mount_root)
        with super().directory() as directory:
            yield directory
