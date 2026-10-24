# MD1.1 — early implemented conversation/identity contract

Implementation checkpoint: commit containing this record. Dependencies:
A M0719c8731ff54c73065f675267556e04d14c17a96;
E verified identity3c32027b60b01320e4c6d4e90d12da0b66128407.
Database schema7. Actual engine remains SQLite3.51.0, not PostgreSQL. E selected
single-instance Railway engineering candidate preserving SQLite; actual account,
private persistent volume, backups/restart and managed-login access remain unverified.
No MD1 hosted acceptance is claimed. Existing D library/migrations1–6 preserved.

## Implemented Python and intended A routes

conversations.Conversations(store) and identity_store.owner_for_identity(store,identity).
Only E auth_adapter.VerifiedIdentity is accepted by mapping; A must call it after
SDK verification. Raw browser mappings rejected401. New issuer+subject atomically
gets fresh stable app_users owner, never an existing anonymous session/profile.
All stored state continues scoped by this owner in the same Store.

D exports conversations.OPERATIONS and dispatch(app,owner,method,path,body).
A alone registers the following. Until registration, endpoints remain unavailable.

| Method/path | Strict input | Response |
| --- | --- | --- |
| GET /api/product/conversations | {} | {contract_version,conversations:[metadata]} Minder only |
| POST /api/product/conversations | {idempotency_key,title?<=120} | {conversation:metadata}; always Minder |
| GET /api/product/conversation | {conversation_id,after_sequence?=0,limit?=100} | History envelope; GET body for internal callers only |
| POST /api/product/conversation | same read body | Same read-only envelope; browser-compatible alias requested from A |
| DELETE /api/product/conversation | {conversation_id,idempotency_key} | {conversation_id,status:'deleted'}; Minder only |
| GET /api/product/mindbot-conversation | {} | History envelope; atomic singleton get/create |
| POST /api/product/conversation-turn | {conversation_id,message<=4000,idempotency_key,expected_profile_version:string|null} | Turn envelope |

Exact validation exports conversation_schemas.SCHEMAS. There is no client channel,
assistant role/outcome, authority, owner or action request in the turn body. Current
profile revision is checked before a new turn, null means no saved Profile. Retry
lookup precedes profile-version checks so an exact old request replays safely after
later edits. Changed retry scope409. Cross-owner targets404; unauthenticated routing
remains A's existing401. Mindbot cannot be deleted or branched409/schema rejection.

Metadata: conversation_id,channel(minder|mindbot),title,version,created_at,updated_at,
status,last_sequence. History: {contract_version,conversation,messages,pending_turns,
has_more,next_after_sequence}. Messages are ascending sequence; read pages<=100.
Message: {message_id,sequence,role,content,created_at,request_id,status,response?}.
Only assistant messages contain response (actual validated server visible DTO).
Opening/listing history never invokes a provider, worker or action.

Turn result: {conversation,turn:{request_id,status,error_code},messages,response}.
Status processing/completed/failed/uncertain is request outcome, not a claimed tool
success. Actual provider/action status remains inside response. Exact completed/failed
retries return persisted outcome without calling model/tools; processing/uncertain
retries return explicit pending state without re-execution. One processing turn per
conversation; another new request409 while live. Processing older than120s becomes
uncertain only on a subsequent begin, never auto-replayed. A new explicit request
can proceed after that; a late original completion can still persist its real result.
No TTL mechanism grants action authority or invents a successful outcome.

## A orchestration callback (no open DB transaction)

D invokes app.conversation_turn_handler(owner,channel,message,history,request_id,body).
Callback must return the validated server-visible response dict. No provider call
is implemented by D. History contains at most12 prior visible messages,<=12000
characters total,<=4000 per message, explicit action/proposal IDs only. Both histories
stay channel/conversation scoped. A must carry stable request_id into action retry
keys and validate the actual tool results; D never reconstructs/replays old commands.

Visible response requires answer (1..20000 chars), max131072 JSON bytes. Top-level
fields: existing ChatResponse answer/statements/provider/profile_version/context_version/
action_status/behaviour_policy_version/integration_mode/diagnostics/response_mode/
conversation_policy_version/conversation_context_id, plus sources/action_ids/
proposal_ids/plan_ids/generation/clarifying_questions/assumptions/status/actions.
Unknown fields rejected; hidden reasoning/prompt/credentials/raw_cv keys rejected.
Explicit action/proposal/plan IDs must resolve to this owner. Source factual
validation remains A's grounding responsibility. Need additional visible fields?
Coordinate an additive D schema refinement, never silently persist internal traces.

A callback failure or missing callback stores a truthful failed assistant result and
safe code; retry does not invoke it again. There is no fake 'Done'. Client may issue
a new reviewed intent after checking actual saved activity. Only actual final visible
responses are retained; no provider reasoning or entire private CV is read/sent here.

## Scheduled result bridge for A/E

Conversations(store).append_notice(owner,event_id,db=None) reads existing persisted
notices and atomically appends one visible assistant message to the same Mindbot
singleton. Unique(owner,event_id) deduplicates concurrent/repeated append. Optional
db enables A to append inside its existing successful worker completion transaction.
Call only after real notice/run persistence; not on history reads. Missing/foreign
notice404. Existing agent_events/notices/settings remain canonical, no new scheduler.
E can reconcile unappended existing notices after a restart, without rerunning jobs.

## Actual checks and next scope

10 focused conversation/identity/migration tests passed, including24 concurrent
Mindbot first loads,16 concurrent verified mappings, new-user/anonymous isolation,
Minder retry/delete/pagination/restart, persisted failed/hidden-response rejection,
shared live SQLite write during deliberately pending callback, exact pending retry,
context follow-up and8 concurrent scheduled appends resolving to one message.
Callbacks in these focused tests are software fixtures, not real-provider evidence.
A owns real model/tool acceptance; E owns real two-account and hosted restart checks.
Next: canonical plan-generation/automation metadata and CV-only library acceptance.

Combined base verification:102 discovered tests,98 passed/4 SDK tests skipped on
legacy Python3.9 (Clerk requires newer Python). The first sandbox run blocked3
existing loopback concurrency tests; elevated rerun passed all runnable tests.
This does not claim live Clerk/login/provider or hosted durability acceptance.
