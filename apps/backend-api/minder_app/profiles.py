"""Explicit edits persist; document/chat interpretation stays a reviewable draft."""
import hashlib
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, now, uid


def save_profile(store, owner, body, expected):
    body = dict(body, profile_id=owner, profile_group_id=owner, version=uid())
    validate("Profile", body)
    try:
        ZoneInfo(body["timezone"])
    except (ZoneInfoNotFoundError, ValueError):
        raise AppError("invalid_timezone") from None
    # The public intake endpoint accepts self-report, never certifies competence.
    for evidence in body["evidence"]:
        if evidence["provenance"]["evidence_type"] not in ("explicit-user", "document-claim", "synthetic-fixture"):
            raise AppError("intake_cannot_certify_evidence")
    with store.transaction() as db:
        # This entry is only reached by a structured direct UI edit, never chat.
        import json
        request_id = uid()
        previous = store.get(owner, "profile", owner, db=db) if expected else None
        db.execute("INSERT INTO authorities VALUES(?,?,?,?)", (owner, request_id,
            json.dumps(dict(kind="explicit_profile_save", expected=expected, profile=body), sort_keys=True), now()))
        result = store.put(owner, "profile", owner, body, expected, db=db)
        from .agents import emit
        if previous:
            for field, trigger in [("constraints", "constraints_changed"), ("preferences", "preferences_changed")]:
                if previous[field] != result[field]:
                    emit(db, owner, request_id + ":" + field, trigger, dict(profile_version=result["version"]))
        return result


def intake_draft(store, owner, *, text, filename=None, content_type="text/plain", channel="chat"):
    if content_type != "text/plain" or (filename and not filename.lower().endswith(".txt")):
        raise AppError("unsupported_document_type_use_utf8_txt", 415)
    if not isinstance(text, str) or not text.strip():
        raise AppError("empty_or_unparsed_document")
    if len(text.encode("utf-8")) > 65536:
        raise AppError("document_too_large", 413)
    draft = dict(id=uid(), channel=channel, status="pending_clarification", text=text,
                 sha256=hashlib.sha256(text.encode()).hexdigest(), created_at=now(),
                 evidence_type="document-claim" if filename else "unconfirmed_chat_claim",
                 clarification="Select the skill/field, describe your evidence, then explicitly save it. "
                               "This text has been read, but no skill mastery has been inferred.")
    with store.transaction() as db:
        db.execute("INSERT INTO drafts VALUES(?,?,?,?)", (owner, draft["id"],
            __import__("json").dumps(draft), draft["status"]))
    return draft
