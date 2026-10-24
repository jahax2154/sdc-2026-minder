# A-R1 / early A-R2 contract — conversation-routing-v1

Current user assigns bounded backend chat/orchestration/runtime repair to A;
OWNERSHIP.json records the transfer from legacy C chat scope at clean3623163.
C's factual grounder/action/worker authority and D migrations remain unchanged.
F retains every frontend file. Read the approved repair brief beside this file.

Verified ancestry: A3a504dc already contains F29281ec, D9f1f2ee and Ec2628ec.
No duplicate merge required. Source frontend is apps/frontend-product; actual A
runtime is8111/9111, F8106/9106. No old acceptance UI is used for this repair.

Observed cause: chat.py forces select_grounded_statements from a closed bundle
containing policy/proposal/limitation records but no application capabilities.
validate_selection always appends limitations/proposal. No model output can answer
an ordinary capability question outside that vocabulary. Missing selected roles
is wrongly treated as a reason for generic limitations even for basic conversation.
F's real baseline (synthetic zero-evidence Profile, model qwen/qwen3.8-27b):
exact capability question15,969ms; repeat16,561ms; available provider/native arguments;
only proposal disclaimer +3limitations,0sources. Navigation during pending chat:
GET profile16,519ms; subsequent four Mindbots reads2–10ms; usable16,595ms vs99/111ms
ordinary repeated navigation (n2, not process-cold). F committed evidence follows.
Static runtime confirms both API/UI use single-request WSGIServer. Provider calls
occur outside SQLite transactions; fix HTTP head-of-line blocking, not write rules.

## Additive request/response, preserve existing evidence envelope

POST /api/chat retains message and optional role/skill selections. Allow
expected_profile_version:null/omitted only when no Profile is saved. A saved Profile
still requires its exact version. No implicit Profile save. Response profile_version
is string `unsaved` for that case, preserving existing client string validation.

Optional request previous_context_id: last response's conversation_context_id.
Only own opaque ledger IDs are accepted; foreign IDs404. Client retains this only
in active in-memory conversation, clears on New chat; no transcript restoration.
Server retains only intent/selection/question scope, never a conversation transcript.
Untrusted previous client prose is not accepted as factual support or authority.

Additive response fields:
- answer:string — actual concise application-authored answer, render FIRST.
- response_mode:application_guidance|grounded_evidence|limited_fallback.
- conversation_policy_version:minder-conversation-routing-v1.
- conversation_context_id:string — opaque owner-scoped previous_context_id token.
- diagnostics:{request_id,intent,reason_codes,context_ms,ledger_ms,provider_ms,total_ms,
  evidence_count,provider_invoked,model}. Metadata only, no raw messages/CVs/profiles.

Existing statements/provider/integration_mode/context_version/profile_version/
behaviour_policy_version/action_status remain. behaviour_policy_version stays
minder-grounding-privacy-v1: external factual grounding is not weakened. Envelope
schema will allow these fields. No new empirical claim category or model prose.

Clear greetings/capability/onboarding and focused workflow follow-ups use verified
application functionality, not market data or a mandatory provider call. Provider
reports unavailable/code provider_not_required_for_application_guidance and
invoked:false; response_mode distinguishes that from an outage. Do not display
'language service unavailable' or 'Language-assisted answer' for this mode.
Available capability descriptions reflect connected services/registered handlers;
disabled storage, temporary chat and unavailable forecasts remain explicit.
Empirical/personal-ranking/market/qualification requests retain existing grounder,
actual provider status and source/date/scope checks. A provider failure yields
limited_fallback, never a claimed successful live interpretation. No chat mutation.

## Timings and concurrency

X-Request-ID and Server-Timing headers correlate requests without user data.
Product launcher will use bounded concurrent WSGI request workers. Existing SQLite
per-request connections/atomic versions/idempotency and provider2-slot budget stay.
No request retry is added. Provider transport remains configured12s, at most one
transient retry +1s backoff (up to25s); backend diagnostics separate context/provider.
Suggested client bounds: ordinary reads8s, writes12s, explicit chat45s. F owns
timeouts/cancellation, section rendering/navigation, pending Working… and safe retry.
Cancelling a browser wait is not proof a server write was undone. Saved Mindbots
reads do not invoke a provider and must finish during a pending chat/provider outage.
