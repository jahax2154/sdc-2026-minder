"""D's executable conversation inputs; A owns publication and HTTP registration."""
from jsonschema import Draft202012Validator
from .store import AppError
from .product_state_schemas import schemas as public_schemas
import json

ID = {"type": "string", "minLength": 1, "maxLength": 200}
SCHEMAS = {
    "create": dict(type="object", additionalProperties=False, required=["idempotency_key"],
        properties=dict(idempotency_key=ID, title={"type": "string", "maxLength": 120})),
    "open": dict(type="object", additionalProperties=False, required=["conversation_id"],
        properties=dict(conversation_id=ID, after_sequence={"type": "integer", "minimum": 0},
                        limit={"type": "integer", "minimum": 1, "maximum": 100})),
    "delete": dict(type="object", additionalProperties=False, required=["conversation_id", "idempotency_key"],
        properties=dict(conversation_id=ID, idempotency_key=ID)),
    "turn": dict(type="object", additionalProperties=False,
        required=["conversation_id", "message", "idempotency_key", "expected_profile_version"],
        properties=dict(conversation_id=ID, idempotency_key=ID,
            message={"type": "string", "minLength": 1, "maxLength": 4000},
            expected_profile_version={"type": ["string", "null"], "maxLength": 200})),
    "search": public_schemas()["ConversationSearch"],
    "empty": dict(type="object", additionalProperties=False),
}
VISIBLE_FIELDS = set("answer statements provider profile_version context_version action_status behaviour_policy_version "
    "integration_mode diagnostics response_mode conversation_policy_version conversation_context_id sources action_ids "
    "proposal_ids plan_ids generation clarifying_questions assumptions status actions".split())


def check(operation, body):
    Draft202012Validator(SCHEMAS[operation]).validate(body)


def visible_response(response):
    if (not isinstance(response, dict) or set(response)-VISIBLE_FIELDS
            or not isinstance(response.get("answer"), str) or not response["answer"].strip()
            or len(response["answer"]) > 20000):
        raise AppError("invalid_visible_conversation_response", 500)
    def scan(value):
        if isinstance(value, dict):
            if set(value).intersection({"reasoning", "chain_of_thought", "api_key", "authorization", "prompt", "raw_cv"}):
                raise AppError("private_internal_response_rejected", 500)
            for item in value.values():
                scan(item)
        elif isinstance(value, list):
            for item in value:
                scan(item)
    scan(response)
    if len(json.dumps(response, allow_nan=False).encode()) > 131072:
        raise AppError("visible_conversation_response_too_large", 500)
    for key in ("action_ids", "proposal_ids", "plan_ids"):
        if key in response and (not isinstance(response[key], list) or len(response[key]) > 20
                or any(not isinstance(item, str) or not item or len(item) > 200 for item in response[key])):
            raise AppError("invalid_conversation_references", 500)
    return response


def validate_search_result(value):
    Draft202012Validator({"$defs":public_schemas(),"$ref":"#/$defs/ConversationSearchResult"}).validate(value)
    return value
