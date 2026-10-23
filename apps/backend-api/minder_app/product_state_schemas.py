"""Product input validation reuses the A-published bootstrap/domain schemas."""
from functools import lru_cache
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from minder_ml.intelligence.service_contracts import validate


@lru_cache(maxsize=1)
def schemas():
    root = Path(__file__).resolve().parents[3]
    result = json.loads((root / "docs/execution/product-v2/contracts.schema.json").read_text())["$defs"]
    text = {"type": "string", "minLength": 1, "maxLength": 200}
    result["ResourceToPlan"] = dict(type="object", additionalProperties=False,
        required=["plan_id", "resource_id", "expected_state_version", "idempotency_key"],
        properties=dict(plan_id=text, resource_id=text, expected_state_version=text,
                        idempotency_key=text))
    result["IntakeCorrection"] = dict(type="object", additionalProperties=False,
        required=["draft_id", "profile", "expected_profile_version", "idempotency_key"],
        properties=dict(draft_id=text, profile={"type": "object"}, idempotency_key=text,
                        expected_profile_version={"type": ["string", "null"]}))
    return result


def check(kind, body):
    schema = schemas()[kind]
    if kind == "TaskCreate":
        # Resolve canonical Task with its established cross-field validator.
        schema = dict(schema, properties=dict(schema["properties"], task={"type": "object"}))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(body)
    if kind == "TaskCreate":
        validate("Task", body["task"])
