"""Explicit edits persist; document/chat interpretation stays a reviewable draft."""
import hashlib
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, now, uid


def save_profile(store, owner, body, expected, *, db=None):
    import json
    import copy
    if not isinstance(body, dict):
        raise AppError("profile_object_required")
    allowed = {"profile_id", "profile_group_id", "version", "synthetic", "evidence",
               "preferences", "current_fields", "constraints", "timezone", "career_context"}
    if set(body) - allowed:
        raise AppError("unknown_profile_field")
    # A partial update merges against the exact expected revision inside the write
    # transaction. Empty arrays explicitly clear input; omitted fields stay unknown.
    if db is None:
        with store.transaction() as conn:
            return save_profile(store, owner, body, expected, db=conn)
    try:
        previous = store.get(owner, "profile", owner, db=db)
    except AppError as error:
        if error.status != 404:
            raise
        previous = None
    if (previous["version"] if previous else None) != expected:
        raise AppError("stale_state_version", 409)
    value = copy.deepcopy(previous) if previous else dict(
        synthetic=False, evidence=[], preferences=[], current_fields=[],
        constraints=[], timezone="Asia/Kuala_Lumpur")
    context = dict(value.get("career_context", {}))
    value.update(copy.deepcopy(body))
    if "career_context" in body and isinstance(body["career_context"], dict):
        context.update(body["career_context"])
        value["career_context"] = context
    value.update(profile_id=owner, profile_group_id=owner, version=uid())
    validate("Profile", value)
    if any(len(value[k]) > 500 for k in ("evidence", "preferences", "current_fields", "constraints")):
        raise AppError("profile_collection_too_large")
    try:
        ZoneInfo(value["timezone"])
    except (ZoneInfoNotFoundError, ValueError):
        raise AppError("invalid_timezone") from None
    for evidence in value["evidence"]:
        if evidence["provenance"]["evidence_type"] not in ("explicit-user", "document-claim", "synthetic-fixture"):
            raise AppError("intake_cannot_certify_evidence")
    request_id = uid()
    db.execute("INSERT INTO authorities VALUES(?,?,?,?)", (owner, request_id,
        json.dumps(dict(kind="explicit_profile_save", expected=expected, profile=value), sort_keys=True), now()))
    result = store.put(owner, "profile", owner, value, expected, db=db)
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
