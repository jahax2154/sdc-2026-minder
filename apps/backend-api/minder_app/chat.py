"""One bounded selection call; application renders source-backed statements only."""
import json
import re
import time
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError
from .store import AppError, uid
from .provider_budget import BudgetedProvider
from .grounding import (POLICY_ID, SYSTEM_POLICY, build_bundle, provider_facts,
                        minimise_question, validate_selection, resolve_claim, verify_bundle)


def chat(store, services, provider, owner, message, expected_profile_version,
         selected_role_ids=None, selected_skill_ids=None, previous_context_id=None, request_id=None, app=None):
    started = time.perf_counter()
    timings = dict(context_ms=0., ledger_ms=0., provider_ms=0.)
    if not isinstance(message, str) or not message.strip() or len(message) > 4000:
        raise AppError("chat_message_required_or_too_large")
    from .conversation import POLICY_ID as CONVERSATION_POLICY, intent_for, selections, matched_roles, guidance, role_quote
    try:
        profile = store.get(owner, "profile", owner)
    except AppError as error:
        if error.status != 404:
            raise
        profile = dict(profile_id=owner, profile_group_id=owner, version='unsaved', synthetic=False,
            evidence=[], preferences=[], current_fields=[], constraints=[], timezone='Asia/Kuala_Lumpur')
    if profile['version'] == 'unsaved' and expected_profile_version not in (None, 'unsaved'):
        raise AppError('stale_state_version', 409)
    if profile['version'] != 'unsaved' and profile["version"] != expected_profile_version:
        raise AppError("stale_state_version", 409)
    previous = {}
    if previous_context_id is not None:
        if not isinstance(previous_context_id, str) or not 1 <= len(previous_context_id) <= 200:
            raise AppError('invalid_previous_context')
        previous = store.get(owner, 'grounding', previous_context_id).get('conversation_scope', {})
    named_roles = matched_roles(services, message)
    if selected_role_ids is None:
        selected_role_ids = named_roles or previous.get('role_ids') or None
    selections(services, selected_role_ids, selected_skill_ids)
    intent = intent_for(message, previous, named_role=bool(named_roles))
    scope = dict(intent=intent, role_ids=selected_role_ids or [], question_id=previous.get('question_id'))
    ledger_id = uid()
    def finish(snapshot, answer, statements, provider_result, mode, reasons):
        return dict(answer=answer, response_mode=mode, conversation_policy_version=CONVERSATION_POLICY,
            conversation_context_id=ledger_id, statements=statements, provider=provider_result,
            integration_mode=services.mode, context_version=snapshot['version'], profile_version=profile['version'],
            behaviour_policy_version=POLICY_ID, action_status='no_mutation_requested_or_executed',
            diagnostics=dict(request_id=request_id or uid(), intent=intent, reason_codes=reasons,
                evidence_count=len(statements), provider_invoked=bool(provider_result.get('invoked', True)),
                model=getattr(provider, 'model', None) or 'not_configured',
                total_ms=round((time.perf_counter()-started)*1000, 3), **timings))
    if intent != 'grounded_evidence':
        statements = []
        quote = role_quote(services, selected_role_ids) if intent == 'role_reference' else None
        if intent == 'role_reference':
            answer = ('Here is the published role description.' if quote else
                      'Which role would you like to understand? Name one or choose a role in Career Match.')
            question_id = 'role'
            capabilities = {}
            if quote:
                statements = [quote]
        else:
            answer, question_id, capabilities = guidance(app, profile, intent, previous)
        scope['question_id'] = question_id
        timings['context_ms'] = round((time.perf_counter()-started)*1000,3)
        ledger_start = time.perf_counter()
        snapshot = store.put(owner, 'grounding', ledger_id, dict(conversation_scope=scope,
            verified_statements=statements, capability_status=capabilities), None)
        timings['ledger_ms'] = round((time.perf_counter()-ledger_start)*1000,3)
        return finish(snapshot, answer, statements,
            dict(status='unavailable', code='provider_not_required_for_verified_reference' if quote else 'provider_not_required_for_application_guidance', invoked=False),
            'grounded_evidence' if quote else 'application_guidance', ['verified_application_or_reference_response'])
    context_start = time.perf_counter()
    context = services.career_context(profile, expected_profile_version=profile["version"],
        selected_role_ids=selected_role_ids, selected_skill_ids=selected_skill_ids)
    timings['context_ms'] = round((time.perf_counter()-context_start)*1000,3)
    ledger_start = time.perf_counter()
    plans = store.list(owner, "plan") if re.search(r"\b(progress|tasks?|roadmap|completed|completion)\b", message, re.I) else []
    # Persist only the bounded claim/support ledger, not another full profile,
    # recommendation matrix, plan graph or raw message/CV. Old snapshots retained.
    ledger = build_bundle(context, services, plans, profile["version"])
    ledger["conversation_scope"] = scope
    snapshot = store.put(owner, "grounding", ledger_id, ledger, None)
    bundle = verify_bundle(store.get(owner, "grounding", ledger_id), services)
    facts = provider_facts(bundle)
    timings['ledger_ms'] = round((time.perf_counter()-ledger_start)*1000,3)
    provider_start = time.perf_counter()
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
    provider_result['invoked'] = provider_result.get('code') not in ('provider_credentials_missing','provider_model_not_configured','provider_context_budget_exceeded','provider_concurrency_limit','provider_daily_budget_exceeded','provider_not_configured')
    timings['provider_ms'] = round((time.perf_counter()-provider_start)*1000,3)
    mode = 'grounded_evidence' if provider_result['status'] == 'available' else 'limited_fallback'
    public = context.get('recommendation', {}).get('public', {}) if context.get('recommendation') else {}
    question = next(iter(public.get('targeted_questions', [])), None)
    answer = ('Here is the verified evidence for your question.' if selected_role_ids else
              'Which role or skill would you like to explore? You can ask general questions without a complete profile.')
    if question and re.search(r'recommend|suitable|fit|career', message, re.I):
        answer = 'A personal assessment needs more specific evidence. ' + question
    if provider_result['status'] != 'available':
        answer = 'The language service is unavailable. The verified saved evidence below remains available; you can retry the explanation later. ' + answer
    return finish(snapshot, answer, selected, provider_result, mode,
                  ['grounded_selection' if mode == 'grounded_evidence' else provider_result.get('code','provider_unavailable')])
