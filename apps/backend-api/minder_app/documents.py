"""Private library over the existing Store and reviewed profile intake."""
import base64
import binascii
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from jsonschema import Draft202012Validator
from .store import AppError, now, uid

CONTRACT_VERSION = "private-document-library-v1"
OPERATIONS = ()  # Published only when the corresponding handlers are implemented.
ID = {"type": "string", "minLength": 1, "maxLength": 200}
SCHEMAS = {
    "upload": dict(type="object", additionalProperties=False,
        required=["filename", "content_type", "content_base64", "idempotency_key"],
        properties=dict(filename={"type": "string", "minLength": 1, "maxLength": 180},
            content_type={"enum": ["application/pdf", "text/plain"]},
            content_base64={"type": "string", "minLength": 1}, idempotency_key=ID)),
    "download": dict(type="object", additionalProperties=False,
        required=["document_id"], properties=dict(document_id=ID)),
    "extract": dict(type="object", additionalProperties=False,
        required=["document_id"], properties=dict(document_id=ID)),
    "delete": dict(type="object", additionalProperties=False,
        required=["document_id", "expected_version", "idempotency_key"],
        properties=dict(document_id=ID, expected_version=ID, idempotency_key=ID)),
}


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
    Draft202012Validator(SCHEMAS["upload"]).validate(body)
    name = body["filename"]
    if name != name.strip() or name in (".", "..") or any(c in name for c in ("/", "\\")) or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise AppError("invalid_document_filename")
    suffix = Path(name).suffix.lower()
    if (suffix, body["content_type"]) not in ((".pdf", "application/pdf"), (".txt", "text/plain")):
        raise AppError("unsupported_document_format", 415)
    if len(body["content_base64"]) > 4*((limits.max_file_bytes+2)//3):
        raise AppError("document_too_large", 413)
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
