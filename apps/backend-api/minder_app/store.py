"""SQLite persistence with atomic expected-version writes and per-user ownership."""
from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import stat
from datetime import datetime, timezone
import uuid


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def uid():
    return str(uuid.uuid4())


class AppError(Exception):
    def __init__(self, code, status=422):
        super().__init__(code)
        self.code, self.status = code, status


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class Store:
    engine = "sqlite"

    def __init__(self, path, *, volume_root=None):
        self.volume_root = None
        self.persistence_mode = "development"
        self.durability_status = "local_unverified"
        if volume_root is not None:
            root = self.verify_volume(volume_root)
            target = Path(path)
            if not target.is_absolute() or not target.resolve().is_relative_to(root):
                raise AppError("database_outside_verified_volume", 500)
            self.volume_root = str(root)
            self.persistence_mode = "mounted-sqlite"
            self.durability_status = "mount_verified_restart_pending"
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY);
            INSERT OR IGNORE INTO migrations VALUES(1);
            CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, owner TEXT NOT NULL,
              created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS documents(owner TEXT, kind TEXT, id TEXT, version TEXT,
              body TEXT NOT NULL, PRIMARY KEY(owner,kind,id));
            CREATE TABLE IF NOT EXISTS history(owner TEXT, kind TEXT, id TEXT, version TEXT,
              body TEXT NOT NULL, created_at TEXT, PRIMARY KEY(owner,kind,id,version));
            CREATE TABLE IF NOT EXISTS drafts(owner TEXT, id TEXT, body TEXT, status TEXT,
              PRIMARY KEY(owner,id));
            ''')

    @staticmethod
    def verify_volume(root):
        root = Path(root)
        if (not root.is_absolute() or root == Path("/") or root.is_symlink()
                or root.resolve() != root or not root.is_dir() or not os.path.ismount(root)):
            raise AppError("persistent_volume_not_verified", 500)
        return root

    @classmethod
    def on_volume(cls, mount_root, database=None):
        root = cls.verify_volume(mount_root)
        return cls(database or root / "minder/runtime.sqlite3", volume_root=root)

    def backup(self, destination):
        """SQLite online snapshot to a new private file; never overwrite a backup."""
        destination = Path(destination)
        if not destination.is_absolute():
            raise AppError("database_backup_absolute_path_required", 500)
        destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except OSError:
            raise AppError("database_backup_target_unavailable", 500) from None
        os.close(fd)
        try:
            with self.connect() as source:
                with sqlite3.connect(str(destination), factory=ClosingConnection) as target:
                    source.backup(target)
        except Exception:
            destination.unlink(missing_ok=True)
            raise AppError("database_backup_failed", 500) from None
        return dict(status="created", engine="sqlite")

    def connect(self):
        if self.volume_root:
            self.verify_volume(self.volume_root)
        db = sqlite3.connect(self.path, timeout=5, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        # Local personal state is plaintext; restrict owned DB/WAL/SHM files,
        # without deleting/rewriting records or claiming encryption/expiry.
        try:
            for name in (self.path, self.path + "-wal", self.path + "-shm"):
                try:
                    fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                except FileNotFoundError:
                    continue
                try:
                    info = os.fstat(fd)
                    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                        raise OSError("not owned regular database")
                    os.fchmod(fd, 0o600)
                finally:
                    os.close(fd)
        except OSError:
            db.close()
            raise AppError("local_database_permissions_failed", 500) from None
        return db

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def session(self):
        token, owner = secrets.token_urlsafe(32), uid()
        with self.transaction() as db:
            db.execute("INSERT INTO sessions VALUES(?,?,?)", (
                hashlib.sha256(token.encode()).hexdigest(), owner, now()))
        return {"token": token, "profile_id": owner}

    def authenticate(self, token):
        if not token:
            raise AppError("authentication_required", 401)
        with self.connect() as db:
            row = db.execute("SELECT owner FROM sessions WHERE token_hash=?", (
                hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        if row is None:
            raise AppError("authentication_required", 401)
        return row["owner"]

    def get(self, owner, kind, doc_id, *, db=None):
        if db is None:
            with self.connect() as conn:
                return self.get(owner, kind, doc_id, db=conn)
        row = db.execute("SELECT body FROM documents WHERE owner=? AND kind=? AND id=?",
                         (owner, kind, doc_id)).fetchone()
        if row is None:
            raise AppError("not_found", 404)
        return json.loads(row["body"])

    def list(self, owner, kind):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute(
                "SELECT body FROM documents WHERE owner=? AND kind=? ORDER BY id", (owner, kind))]

    def put(self, owner, kind, doc_id, body, expected, *, db=None):
        if db is None:
            with self.transaction() as conn:
                return self.put(owner, kind, doc_id, body, expected, db=conn)
        row = db.execute("SELECT version FROM documents WHERE owner=? AND kind=? AND id=?",
                         (owner, kind, doc_id)).fetchone()
        if (row[0] if row else None) != expected:
            raise AppError("stale_state_version", 409)
        value = copy.deepcopy(body)
        version = uid()
        value["state_version" if kind == "plan" else "version"] = version
        if kind == "plan":
            value["previous_version"] = expected
        encoded = json.dumps(value, sort_keys=True, allow_nan=False)
        db.execute("INSERT OR REPLACE INTO documents VALUES(?,?,?,?,?)",
                   (owner, kind, doc_id, version, encoded))
        db.execute("INSERT INTO history VALUES(?,?,?,?,?,?)",
                   (owner, kind, doc_id, version, encoded, now()))
        return value
