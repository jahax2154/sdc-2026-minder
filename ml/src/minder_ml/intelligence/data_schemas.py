"""Canonical V1 entities. Schema validity is not human approval or empirical evidence."""

from datetime import date
from functools import lru_cache
import json
import math
from pathlib import Path

VERSION = "minder-data-v1"
ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "contracts/data-entities.v1.schema.json"


@lru_cache()
def validator():
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


@lru_cache()
def entity_validator(kind):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = validator().schema
    if kind not in {"UserProfile", "RoleDefinition", "PersonalFitAnnotation", "MarketObservation", "RoleMarketCrosswalk", "SkillTaxonomyCrosswalk"}:
        raise ValueError("unknown canonical entity_type")
    return Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/" + kind}, format_checker=FormatChecker())


def _finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite numbers are not canonical JSON")
    if isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)


def validate_entity(record, expected=None):
    from jsonschema import ValidationError
    if not isinstance(record, dict):
        raise ValueError("canonical entity must be a JSON object")
    _finite(record)
    try:
        entity_validator(record.get("entity_type")).validate(record)
    except ValidationError as exc:
        raise ValueError("canonical schema: " + exc.message) from exc
    kind = record["entity_type"]
    if expected is not None and kind != expected:
        raise ValueError("unexpected entity type")
    if kind == "MarketObservation":
        start, end = date.fromisoformat(record["period_start"]), date.fromisoformat(record["period_end"])
        if end < start:
            raise ValueError("period_end precedes period_start")
        if record["frequency"] == "quarterly":
            from calendar import monthrange
            month = start.month + 2
            if start.month not in (1, 4, 7, 10) or start.day != 1 or end != date(start.year, month, monthrange(start.year, month)[1]):
                raise ValueError("quarterly window must be an actual calendar quarter")
        if record["frequency"] == "annual" and (start != date(start.year, 1, 1) or end != date(start.year, 12, 31)):
            raise ValueError("annual window must be a complete labelled year")
        if record["value"] is None and record["data_quality_status"] != "missing":
            raise ValueError("unknown value must have missing status")
        if record["value"] is not None and record["data_quality_status"] == "missing":
            raise ValueError("missing status cannot contain an invented numeric value")
        if record["indicator_id"] == "online_job_offerings" and record["value"] is not None and (
            record["value"] < 0 or record["value"] != int(record["value"])
        ):
            raise ValueError("offering counts must be nonnegative integers")
    elif kind == "RoleDefinition":
        ids = [c["criterion_id"] for c in record["criteria"]]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate criterion_id")
        effort = record["remaining_effort"]
        low, high, used = (effort[n] for n in ("low_hours", "high_hours", "hours_used"))
        if low is not None and high is not None and low > high:
            raise ValueError("reversed effort range")
        if used is not None and ((low is not None and used < low) or (high is not None and used > high)):
            raise ValueError("selected effort outside reviewed range")
        if record["review"]["status"] == "approved":
            required = record["criteria"]
            if not record["preparation_milestone"] or not required or any(
                c["review"]["status"] != "approved" or c["requirement_weight"] is None or not c["observable_evidence_rule"]
                for c in required
            ) or sum(c["requirement_weight"] for c in required) <= 0:
                raise ValueError("approved role requires approved observable criteria and positive total weight")
            if (not record["occupation_identifiers"] or any(m["review"]["status"] != "approved" for m in record["occupation_identifiers"])
                    or any(r["review"]["status"] != "approved" or not r["definition"] or not r["evidence_rule"] for r in record["feature_rubrics"].values())
                    or effort["review"]["status"] != "approved"):
                raise ValueError("approved role requires reviewed mappings, rubrics and effort")
    elif kind == "PersonalFitAnnotation":
        if record["review_status"] == "approved" and (
            record["label_source"] != "human_reviewed" or record["grade"] is None
            or not record["reviewer_id"] or not record["rationale"] or not record["reviewed_at"]
            or record["independent_review"] is not True
        ):
            raise ValueError("gold approval requires an independent human review and provenance")
        if record["grade"] is not None and record["label_source"] is None:
            raise ValueError("a grade requires a declared label source")
    return record


def pending_review():
    return {"status": "pending", "reviewer_id": None, "rationale": None, "reviewed_at": None}
