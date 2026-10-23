"""E-owned additive read contracts; shared ProductView remains authoritative."""
from jsonschema import validate

VERSION = "product-v2-bootstrap-v1"
READ_VERSION = "product-reads-v1"
VIEW_REQUEST = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "selected_role_ids": {"type": "array", "maxItems": 3, "uniqueItems": True,
                              "items": {"type": "string"}},
        "selected_skill_ids": {"type": "array", "maxItems": 3, "uniqueItems": True,
                               "items": {"type": "string"}},
        "plan_id": {"type": "string", "minLength": 1},
        "state": {"enum": ["proposed", "scheduled", "completed", "cancelled"]},
        "scheduled_from": {"type": "string", "format": "date-time"},
        "scheduled_to": {"type": "string", "format": "date-time"},
        "offset": {"type": "integer", "minimum": 0},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
    },
}


def validate_view_request(body):
    validate(body, VIEW_REQUEST)


def envelope(view, profile, data, limitations=(), status="available"):
    return dict(contract_version=VERSION, read_version=READ_VERSION, view=view,
                status=status, profile_version=profile["version"] if profile else None,
                data=data, limitations=list(limitations))
