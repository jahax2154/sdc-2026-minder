"""One bounded selection call; application renders source-backed statements only."""
import json
import re
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError
from .store import AppError, uid
from .provider_budget import BudgetedProvider
from .grounding import (POLICY_ID, SYSTEM_POLICY, build_bundle, provider_facts,
                        minimise_question, validate_selection, resolve_claim, verify_bundle)


def chat(store, services, provider, owner, message, expected_profile_version,
         selected_role_ids=None, selected_skill_ids=None):
    if not isinstance(message, str) or not message.strip() or len(message) > 4000:
        raise AppError("chat_message_required_or_too_large")
    profile = store.get(owner, "profile", owner)
    if profile["version"] != expected_profile_version:
        raise AppError("stale_state_version", 409)
    context = services.career_context(profile, expected_profile_version=expected_profile_version,
        selected_role_ids=selected_role_ids, selected_skill_ids=selected_skill_ids)
    plans = store.list(owner, "plan") if re.search(r"\b(progress|tasks?|roadmap|completed|completion)\b", message, re.I) else []
    # Persist only the bounded claim/support ledger, not another full profile,
    # recommendation matrix, plan graph or raw message/CV. Old snapshots retained.
    ledger_id = uid()
    snapshot = store.put(owner, "grounding", ledger_id,
        build_bundle(context, services, plans, profile["version"]), None)
    bundle = verify_bundle(store.get(owner, "grounding", ledger_id), services)
    facts = provider_facts(bundle)
    selected = [resolve_claim(c, bundle) for c in bundle["claims"]]
    provider_result = {"status": "unavailable", "code": "provider_not_configured"}
    try:
        tool = {"type": "function", "function": {"name": "select_grounded_statements",
            "description": "Select saved evidence statements for application rendering; never mutate state.",
            "parameters": {"type": "object", "additionalProperties": False,
                "properties": {"statement_ids": {"type": "array", "minItems": 1, "maxItems": len(facts),
                    "uniqueItems": True, "items": {"type": "string", "enum": [f["id"] for f in facts]}}},
                "required": ["statement_ids"]}}}
        result = BudgetedProvider(store, owner, provider or GroqAdapter()).complete_tool([
            {"role": "system", "content": SYSTEM_POLICY},
            {"role": "user", "content": json.dumps({"question": minimise_question(message), "facts": facts})}], tool)
        selected = validate_selection(result["text"], bundle)
        provider_result = {k: v for k, v in result.items() if k != "text"}
    except ProviderError as exc:
        provider_result = exc.public()
    except (ValueError, TypeError, KeyError):
        provider_result = {"status": "unavailable", "code": "provider_ungrounded_response_rejected"}
    return dict(statements=selected, provider=provider_result, integration_mode=services.mode,
                context_version=snapshot["version"], profile_version=profile["version"],
                behaviour_policy_version=POLICY_ID,
                action_status="no_mutation_requested_or_executed")
