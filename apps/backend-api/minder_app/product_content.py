"""Small metadata-only feed using C's source-verified library.

No user-controlled URL fetch, provider request or generated summary. Retrieval dates
are the library's original observations, never the time this view is opened.
"""
from jsonschema import validate
from urllib.parse import urlsplit
from .resources import learning_options
from .store import AppError

OPERATIONS = {("POST", "/api/product/resources"), ("POST", "/api/product/resource-detail")}
REQUEST = {"type": "object", "additionalProperties": False, "properties": {
    "topic_ids": {"type": "array", "maxItems": 20, "uniqueItems": True, "items": {"type": "string"}},
    "types": {"type": "array", "uniqueItems": True,
              "items": {"enum": ["learning_resource", "article", "video"]}},
    "publishers": {"type": "array", "maxItems": 20, "items": {"type": "string"}},
    "published_from": {"type": "string", "format": "date"},
    "published_to": {"type": "string", "format": "date"},
    "offset": {"type": "integer", "minimum": 0},
    "limit": {"type": "integer", "minimum": 1, "maximum": 50},
}}
APPROVED_HOSTS = {"docs.python.org", "learn.microsoft.com"}


def catalogue():
    library = learning_options()
    result, seen = [], set()
    for original in library["resources"]:
        uri = original["source"]["uri"]
        parsed = urlsplit(uri)
        if (parsed.scheme != "https" or parsed.hostname not in APPROVED_HOSTS
                or parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise AppError("resource_source_invalid", 500)
        canonical = parsed._replace(fragment="", netloc=parsed.hostname).geturl().rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        result.append(dict(original, type="learning_resource", published_at=None,
                           retrieved_at=original["source"]["available_at"],
                           summary=None, summary_status="metadata_only_no_generated_summary",
                           language=None, url=uri, canonical_url=canonical))
    return library["version"], result


def resource_list(app, owner, body):
    validate(body, REQUEST)
    from datetime import date
    for key in ("published_from", "published_to"):
        if key in body:
            date.fromisoformat(body[key])
    if body.get("published_from", "") > body.get("published_to", "9999-12-31"):
        raise AppError("invalid_publication_range")
    version, items = catalogue()
    from .product_views import optional_document, state_read
    profile = optional_document(app.store, owner, "profile", owner)
    known = {topic for item in items for topic in item["topic_ids"]}
    explicit = set(body.get("topic_ids", []))
    # Exact canonical topic IDs only; no free-text/private data is sent anywhere.
    inferred = {e["subject_id"] for e in profile["evidence"] if e["subject_id"] in known} if profile else set()
    relevant = explicit or inferred
    selected = []
    for item in items:
        if explicit and not explicit.intersection(item["topic_ids"]):
            continue
        if "types" in body and item["type"] not in body["types"]:
            continue
        if "publishers" in body and item["publisher"] not in body["publishers"]:
            continue
        # Unknown publication dates cannot satisfy a dated-news filter.
        if "published_from" in body or "published_to" in body:
            continue
        matched = sorted(relevant.intersection(item["topic_ids"]))
        selected.append(dict(item, matched_topic_ids=matched,
            relevance_reason=("Exact topic match: " + ", ".join(matched)) if matched else
                             "General verified learning option; no role or skill-gap mapping asserted."))
    selected.sort(key=lambda item: (not bool(item["matched_topic_ids"]), item["resource_id"]))
    offset, limit = body.get("offset", 0), body.get("limit", 20)
    return dict(contract_version="product-content-v1", catalogue_version=version,
        status="available" if selected else "empty", resources=selected[offset:offset + limit],
        total=len(selected), offset=offset, next_offset=offset + limit if offset + limit < len(selected) else None,
        order="exact_topic_match_then_resource_id; not market demand", profile_version=profile["version"] if profile else None,
        interactions=state_read(app, owner, "resource-state"),
        coverage={"learning_resource": len(items), "article": 0, "video": 0},
        cache={"mode": "versioned_verified_metadata", "revalidated_on_request": False,
               "retrieved_at": sorted({i["retrieved_at"] for i in items})},
        limitations=["Small C source library; no news or video feed is integrated.",
                     "Publication dates, duration, total cost and language remain unknown.",
                     "Cached metadata does not guarantee current access or availability.",
                     "Learning activity does not certify mastery or employer suitability."])


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS:
        raise AppError("not_found", 404)
    if path.endswith("/resource-detail"):
        validate(body, {"type": "object", "additionalProperties": False,
                        "required": ["resource_id"], "properties": {"resource_id": {"type": "string"}}})
        version, items = catalogue()
        item = next((i for i in items if i["resource_id"] == body["resource_id"]), None)
        if item is None:
            raise AppError("resource_not_found", 404)
        return dict(contract_version="product-content-v1", catalogue_version=version, resource=item)
    return resource_list(app, owner, body)
