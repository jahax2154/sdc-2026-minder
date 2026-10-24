"""Private library over the existing Store and reviewed profile intake."""
import base64
import binascii
from dataclasses import asdict, dataclass
import hashlib
import json
import os
import importlib.util
import subprocess
import sys
import threading
from pathlib import Path
import re
import uuid
from jsonschema import Draft202012Validator
from .store import AppError, now, uid
from .product_state_schemas import schemas as public_schemas

CONTRACT_VERSION = "private-document-library-v1"

# A's published request definitions are the only structural authority.
SCHEMAS = {"upload": public_schemas()["DocumentUpload"],
           "download": public_schemas()["DocumentRead"],
           "extract": public_schemas()["DocumentRead"],
           "delete": public_schemas()["DocumentDelete"]}


@dataclass(frozen=True)
class DocumentLimits:
    max_file_bytes: int = 65536
    max_files: int = 10
    max_user_bytes: int = 524288

    def __post_init__(self):
        for value, maximum in ((self.max_file_bytes, 1024*1024), (self.max_files, 100),
                               (self.max_user_bytes, 64*1024*1024)):
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                raise AppError("invalid_document_limits", 500)

    @property
    def upload_request_bytes(self):
        return max(131072, 4*((self.max_file_bytes+2)//3) + 4096)

    @classmethod
    def from_environment(cls, environ=None):
        env = os.environ if environ is None else environ
        try:
            return cls(**{field: int(env.get("MINDER_DOCUMENT_" + field.upper(), default))
                          for field, default in asdict(cls()).items()})
        except (TypeError, ValueError):
            raise AppError("invalid_document_limits", 500) from None


def validate_upload(body, limits):
    if (isinstance(body, dict) and isinstance(body.get("content_base64"), str)
            and len(body["content_base64"]) > 4*((limits.max_file_bytes+2)//3)):
        raise AppError("document_too_large", 413)
    Draft202012Validator(SCHEMAS["upload"]).validate(body)
    name = body["filename"]
    if name != name.strip() or name in (".", "..") or any(c in name for c in ("/", "\\")) or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise AppError("invalid_document_filename")
    suffix = Path(name).suffix.lower()
    if (suffix, body["content_type"]) not in ((".pdf", "application/pdf"), (".txt", "text/plain")):
        raise AppError("unsupported_document_format", 415)
    try:
        content = base64.b64decode(body["content_base64"], validate=True)
    except (binascii.Error, ValueError):
        raise AppError("invalid_document_encoding") from None
    if len(content) > limits.max_file_bytes:
        raise AppError("document_too_large", 413)
    if not content:
        raise AppError("empty_document")
    if suffix == ".pdf":
        # A bounded signature check, never a safety or full PDF parsing claim.
        if not re.match(br"%PDF-[12]\.[0-9]", content) or b"%%EOF" not in content[-1024:]:
            raise AppError("invalid_pdf_document", 415)
    else:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeError:
            raise AppError("document_requires_utf8_text", 415) from None
        if not text.strip() or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
            raise AppError("invalid_text_document", 415)
    return content


def upload_request_limit():
    """A's WSGI boundary reads only trusted, bounded server configuration."""
    return DocumentLimits.from_environment().upload_request_bytes


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


class DocumentLibrary:
    def __init__(self, store, storage=None, limits=None):
        self.store, self.storage = store, storage
        self.limits = limits or DocumentLimits()
        from .product_migrations import migrate
        migrate(store)

    @classmethod
    def from_environment(cls, store, environ=None):
        env = os.environ if environ is None else environ
        limits = DocumentLimits.from_environment(env)
        mode = env.get("MINDER_DOCUMENT_STORAGE", "disabled")
        storage = None
        if mode == "local-development":
            from .document_storage import LocalDocumentStorage
            uploads = Path(store.path).resolve().parent / "uploads"
            root = Path(env.get("MINDER_DOCUMENT_STORAGE_ROOT", str(uploads / "documents")))
            if not root.is_absolute() or not root.resolve().is_relative_to(uploads.resolve()):
                raise AppError("document_storage_root_outside_lane_uploads", 500)
            storage = LocalDocumentStorage(root)
        elif mode == "private-volume":
            from .document_storage import PrivateVolumeDocumentStorage
            if not getattr(store, "volume_root", None):
                raise AppError("document_storage_requires_verified_database_volume", 500)
            root = Path(env.get("MINDER_DOCUMENT_STORAGE_ROOT", str(Path(store.path).parent / "documents")))
            storage = PrivateVolumeDocumentStorage(store.volume_root, root)
        elif mode == "replit-app-storage":
            from .document_storage import ReplitAppStorage
            if getattr(store, "engine", None) != "postgresql":
                raise AppError("replit_document_storage_requires_postgresql", 503)
            storage = ReplitAppStorage.from_environment(env)
            storage.probe() # Fail explicitly when configured bucket read access is unavailable.
        elif mode != "disabled":
            raise AppError("document_storage_backend_not_configured", 500)
        return cls(store, storage, limits)

    def backend(self):
        if self.storage is None:
            raise AppError("document_storage_not_configured", 500)
        return self.storage

    @staticmethod
    def public(row):
        metadata = {key: value for key, value in json.loads(row["body"]).items() if not key.startswith("_")}
        if metadata.get("status") != "deleted":
            metadata.setdefault("purpose", "legacy_unclassified")
        return metadata

    def owned(self, db, owner, document_id, *, active=False):
        row = db.execute("SELECT * FROM library_documents WHERE owner=? AND id=?",
                         (owner, document_id)).fetchone()
        if row is None or row["status"] == "deleted":
            raise AppError("document_not_found", 404)
        if active and row["status"] != "active":
            raise AppError("document_not_available", 409)
        return row

    def receipt(self, db, owner, key, operation, scope):
        row = db.execute("SELECT * FROM library_requests WHERE owner=? AND key=?", (owner, key)).fetchone()
        if row and (row["operation"] != operation or row["scope_hash"] != scope):
            raise AppError("idempotency_scope_conflict", 409)
        return row

    def list(self, owner):
        with self.store.connect() as db:
            rows = list(db.execute("SELECT * FROM library_documents WHERE owner=? AND status<>'deleted' "
                                   "ORDER BY created_at,id", (owner,)))
        return dict(contract_version=CONTRACT_VERSION, documents=[self.public(row) for row in rows],
            limits=dict(asdict(self.limits), upload_request_bytes=self.limits.upload_request_bytes),
            storage=dict(status="available" if self.storage else "unavailable",
                mode=getattr(self.storage, "mode", "disabled"), durable_hosting_verified=False,
                durability_status=getattr(self.storage, "durability_status", "local_unverified" if self.storage else "unavailable")),
            usage=dict(file_count=len(rows), stored_or_reserved_bytes=sum(row["byte_size"] for row in rows)),
            extraction=dict(supported_types=["text/plain"] + (["application/pdf"] if pdf_available() else []),
                            max_text_bytes=65536, max_pdf_pages=20,
                            pdf_status="supported_text_only" if pdf_available() else "unavailable",
                            automatic_profile_apply=False, purpose="user_declared_cv_or_resume"))

    def upload(self, owner, body):
        content = validate_upload(body, self.limits)
        backend = self.backend()
        # Hash the full request; no base64 bytes/text enter metadata, audit or receipts.
        scope = fingerprint(body)
        key = body["idempotency_key"]
        with self.store.transaction() as db:
            receipt = self.receipt(db, owner, key, "upload", scope)
            if receipt:
                document_id = receipt["document_id"]
                row = self.owned(db, owner, document_id)
                if row["status"] == "deleting":
                    raise AppError("document_not_available", 409)
                if row["status"] == "active":
                    return dict(document=self.public(row))
            else:
                usage = db.execute("SELECT count(*),coalesce(sum(byte_size),0) FROM library_documents "
                                   "WHERE owner=? AND status<>'deleted'", (owner,)).fetchone()
                if usage[0] >= self.limits.max_files or usage[1]+len(content) > self.limits.max_user_bytes:
                    raise AppError("document_owner_limit_exceeded", 413)
                document_id, version = uid(), uid()
                metadata = dict(document_id=document_id, version=version, filename=body["filename"],
                    content_type=body["content_type"], purpose=body["purpose"],
                    purpose_basis="user_declared_not_independently_verified", size_bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
                    created_at=now(), status="uploading",
                    extraction_status="not_requested" if (body["content_type"] == "text/plain" and len(content) <= 65536)
                        or (body["content_type"] == "application/pdf" and pdf_available()) else "unavailable",
                    _storage_key=uuid.uuid4().hex)
                db.execute("INSERT INTO library_documents VALUES(?,?,?,?,?,?,?)", (owner, document_id,
                    version, "uploading", encoded(metadata), len(content), metadata["created_at"]))
                db.execute("INSERT INTO library_requests VALUES(?,?,?,?,?)", (owner, key, "upload", scope, document_id))
        # Reserve first, then hold the DB writer lock while finalizing immutable
        # bytes. A crash/failure leaves an observable retryable uploading row.
        with self.store.transaction() as db:
            row = self.owned(db, owner, document_id)
            if row["status"] == "active":
                return dict(document=self.public(row))
            if row["status"] != "uploading":
                raise AppError("document_not_available", 409)
            metadata = json.loads(row["body"])
            backend.put(metadata["_storage_key"], content)
            metadata.update(status="active", version=uid())
            db.execute("UPDATE library_documents SET status='active',version=?,body=? WHERE owner=? AND id=?",
                       (metadata["version"], encoded(metadata), owner, document_id))
            return dict(document=self.public(dict(body=encoded(metadata))))

    def checked_content(self, row):
        metadata = json.loads(row["body"])
        content = self.backend().get(metadata["_storage_key"], metadata["size_bytes"])
        if len(content) != metadata["size_bytes"] or hashlib.sha256(content).hexdigest() != metadata["sha256"]:
            raise AppError("document_storage_integrity_failed", 500)
        return content

    def download(self, owner, body):
        Draft202012Validator(SCHEMAS["download"]).validate(body)
        # Serialize with deletion, so a completed deletion cannot serve stale bytes.
        with self.store.transaction() as db:
            row = self.owned(db, owner, body["document_id"], active=True)
            content = self.checked_content(row)
            return dict(document=self.public(row), content_base64=base64.b64encode(content).decode("ascii"),
                        download_content_type="application/octet-stream")

    def delete(self, owner, body):
        Draft202012Validator(SCHEMAS["delete"]).validate(body)
        scope, key = fingerprint(body), body["idempotency_key"]
        with self.store.transaction() as db:
            receipt = self.receipt(db, owner, key, "delete", scope)
            if receipt:
                row = db.execute("SELECT * FROM library_documents WHERE owner=? AND id=?",
                                 (owner, receipt["document_id"])).fetchone()
                if row["status"] == "deleted":
                    return self.public(row)
            else:
                row = self.owned(db, owner, body["document_id"])
                if row["version"] != body["expected_version"]:
                    raise AppError("stale_state_version", 409)
                if row["status"] == "deleting":
                    raise AppError("document_deletion_in_progress", 409)
                metadata = json.loads(row["body"])
                metadata.update(status="deleting", version=uid())
                db.execute("UPDATE library_documents SET status='deleting',version=?,body=? WHERE owner=? AND id=?",
                           (metadata["version"], encoded(metadata), owner, body["document_id"]))
                db.execute("INSERT INTO library_requests VALUES(?,?,?,?,?)",
                           (owner, key, "delete", scope, body["document_id"]))
                # Quarantine derived review input immediately, even if object deletion
                # later fails. Already applied profile/history is a separate record.
                db.execute("DELETE FROM drafts WHERE owner=? AND id IN "
                           "(SELECT draft_id FROM library_drafts WHERE owner=? AND document_id=?)",
                           (owner, owner, body["document_id"]))
                db.execute("DELETE FROM library_drafts WHERE owner=? AND document_id=?", (owner, body["document_id"]))
        with self.store.transaction() as db:
            row = db.execute("SELECT * FROM library_documents WHERE owner=? AND id=?",
                             (owner, body["document_id"])).fetchone()
            if row["status"] == "deleted":
                return self.public(row)
            metadata = json.loads(row["body"])
            self.backend().delete(metadata["_storage_key"])
            tombstone = dict(document_id=body["document_id"], status="deleted", deleted_at=now())
            db.execute("UPDATE library_documents SET status='deleted',body=?,byte_size=0,version=? WHERE owner=? AND id=?",
                       (encoded(tombstone), uid(), owner, body["document_id"]))
            return tombstone

    def extract(self, owner, body):
        Draft202012Validator(SCHEMAS["extract"]).validate(body)
        with self.store.connect() as db:
            row = self.owned(db, owner, body["document_id"], active=True)
            metadata = json.loads(row["body"])
            link = db.execute("SELECT draft_id FROM library_drafts WHERE owner=? AND document_id=?",
                              (owner, body["document_id"])).fetchone()
            if link:
                draft_row = db.execute("SELECT body FROM drafts WHERE owner=? AND id=?", (owner, link["draft_id"])).fetchone()
                if draft_row is None:
                    raise AppError("document_intake_record_missing", 409)
                return dict(document=self.public(row), extraction=dict(status="review_available", manual_entry_available=True),
                            draft=json.loads(draft_row["body"]))
            content = None
            reason = None
            if metadata.get("purpose") not in ("cv", "resume"):
                reason = "legacy_document_purpose_unclassified"
            elif metadata["content_type"] == "text/plain" and metadata["size_bytes"] > 65536:
                reason = "text_exceeds_reviewed_intake_limit"
            elif metadata["content_type"] == "application/pdf" and not pdf_available():
                reason = "pdf_text_extraction_not_supported"
            else:
                content = self.checked_content(row)
        # Parsing can be slow/untrusted. No DB transaction or server secrets cross
        # into its bounded child process; it cannot block profile/worker writes.
        text = None
        if content is not None:
            if metadata["content_type"] == "application/pdf":
                text, reason = extract_pdf(content)
            else:
                text = content.decode("utf-8-sig")
        with self.store.transaction() as db:
            row = self.owned(db, owner, body["document_id"], active=True)
            metadata = json.loads(row["body"])
            draft = None
            if text is not None:
                link = db.execute("SELECT draft_id FROM library_drafts WHERE owner=? AND document_id=?",
                                  (owner, body["document_id"])).fetchone()
                if link:
                    draft = json.loads(db.execute("SELECT body FROM drafts WHERE owner=? AND id=?", (owner, link["draft_id"])).fetchone()[0])
                else:
                    from .profiles import _intake_draft
                    draft = _intake_draft(db, owner, text=text,
                        filename=Path(metadata["filename"]).stem+".txt", channel="cv-resume-library")
                    draft.update(source_document_id=metadata["document_id"], source_content_type=metadata["content_type"],
                                 source_sha256=metadata["sha256"])
                    db.execute("UPDATE drafts SET body=? WHERE owner=? AND id=?", (encoded(draft),owner,draft["id"]))
                    db.execute("INSERT INTO library_drafts VALUES(?,?,?)", (owner, body["document_id"], draft["id"]))
                status = "review_available"
            else:
                status = "unavailable"
            if metadata["extraction_status"] != status:
                metadata.update(extraction_status=status, version=uid())
                db.execute("UPDATE library_documents SET body=?,version=? WHERE owner=? AND id=?",
                           (encoded(metadata), metadata["version"], owner, body["document_id"]))
            extraction = dict(status=status, manual_entry_available=True)
            if reason:
                extraction["reason"] = reason
            return dict(document=self.public(dict(body=encoded(metadata))), extraction=extraction, draft=draft)


OPERATIONS = (("GET", "/api/product/documents"),) + tuple(
    ("POST", "/api/product/document-" + operation) for operation in ("upload", "download", "delete", "extract"))


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS:
        raise AppError("product_capability_unavailable", 404)
    library = getattr(app, "document_library", None)
    if library is None:
        library = app.document_library = DocumentLibrary.from_environment(app.store)
    if method == "GET":
        Draft202012Validator(dict(type="object", additionalProperties=False)).validate(body)
        return library.list(owner)
    operation = path.rsplit("-", 1)[-1]
    return getattr(library, operation)(owner, body)



def pdf_available():
    return importlib.util.find_spec("pypdf") is not None


_PDF_SLOTS = threading.BoundedSemaphore(2)


def extract_pdf(content):
    if not _PDF_SLOTS.acquire(blocking=False):
        return None, "pdf_extraction_busy"
    child_env = {key: os.environ[key] for key in ("PATH", "PYTHONPATH", "LANG") if key in os.environ}
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run([sys.executable, "-B", "-m", "minder_app.documents", "--extract-pdf"],
            input=content, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12, env=child_env)
        if result.returncode != 0 or len(result.stdout) > 131072:
            return None, "pdf_extraction_budget_or_parse_failed"
        parsed = json.loads(result.stdout)
        text = parsed.get("text")
        if text is not None and (not isinstance(text,str) or len(text.encode("utf-8")) > 65536):
            return None, "pdf_extracted_text_too_large"
        return text, parsed.get("reason")
    except (subprocess.TimeoutExpired, OSError, ValueError, TypeError):
        return None, "pdf_extraction_unavailable"
    finally:
        _PDF_SLOTS.release()


def _pdf_worker():
    import io
    import logging
    logging.disable(logging.CRITICAL)
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (5,5))
        if sys.platform.startswith("linux"):
            resource.setrlimit(resource.RLIMIT_AS, (384*1024*1024,384*1024*1024))
        from pypdf import PdfReader
        raw = sys.stdin.buffer.read(1048577)
        if len(raw) > 1048576:
            raise ValueError()
        reader = PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted:
            output = dict(reason="pdf_encrypted_not_supported")
        elif len(reader.pages) > 20:
            output = dict(reason="pdf_page_limit_exceeded")
        else:
            parts, size = [],0
            for page in reader.pages:
                stream = page.get_contents()
                if stream is not None and len(stream.get_data()) > 2*1024*1024:
                    raise ValueError()
                text = page.extract_text() or ""
                text = "".join(c for c in text if ord(c)>=32 or c in "\n\r\t")
                size += len(text.encode("utf-8"))+1
                if size > 65536:
                    print(json.dumps(dict(reason="pdf_extracted_text_too_large")))
                    return
                parts.append(text)
            text = "\n".join(parts).strip()
            output = dict(text=text) if text else dict(reason="pdf_no_extractable_text")
    except Exception:
        output = dict(reason="pdf_parse_failed")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__" and sys.argv[1:] == ["--extract-pdf"]:
    _pdf_worker()
