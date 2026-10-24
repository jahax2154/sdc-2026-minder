# M0 — Revision 3 independent lane release

Authority: docs/Minder_Morning_Completion_Runbook_2026-10-24.md, Revision 3.
Verified integrated starting HEAD: 12856703ef187b09cbcb857b85923890fef331c4.
Contains F8446ca801de8d8a0163c390f76d2aa609a5fec16, D9f1f2eeabb8d5d8247fcc1b0353a8777d690d71e,
Ec2628eceaf4700cd124a407ec4dfe43a6cdbd4ff, Bd9ffd4f3cc7625c736ea081c52da3c1122b21c08.
The containing M0 commit is the immutable dependency; use the published full SHA.
Do not reset, redo bootstrap or replace lane work. Merge only missing committed history.

## Launch now

D, E and F are released for independent implementation under OWNERSHIP.json.
The user launches/resumes their existing sessions; no additional agent is needed.
Read this Revision 3 and ownership rather than superseded P0 launch deferrals.
D publishes the first conversation/identity slice early; E publishes isolated auth
verification/config early; F starts approved designs and shared client adapters now.

| Lane | Absolute directory | Branch | API/UI | Outputs / database |
| --- | --- | --- | --- | --- |
| A | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-a | session/a-personal-integration | 8111/9111 | ml/artifacts/session-a/product/runtime.sqlite3 |
| D | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-d | session/d-profile-state | 8104/9104 | ml/artifacts/session-d/product/runtime.sqlite3 |
| E | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-e | session/e-explore-resources | 8105/9105 | ml/artifacts/session-e/product/runtime.sqlite3 |
| F | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-f | session/f-product-frontend | 8106/9106 | ml/artifacts/session-f/product/runtime.sqlite3 |

Paths relative to each lane root. Logs/uploads/output stay in that lane's product
artifact directory. Existing databases/other runtimes stay untouched. No worker
starts automatically. D is the sole migration/schema writer, including Store.

```sh
# In YOUR existing lane worktree; select YOUR lane, do not use another DB.
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D --check
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests
```

Substitute E/F/A for D. Interpreter is the existing Python3.9 environment, read-only.
Do not recreate it, recopy credentials or alter pinned source inputs. A/F secure
server config retains actual model `qwen/qwen3.8-27b`. Secrets never enter Git,
logs, frontend config or bundles. E/D can develop without model access.

## Existing contracts — implemented, with explicit gaps

- Actual WSGI Application.dispatch(method,path,body,token,request_id=...).
  POST /api/session currently issues anonymous bearer capability. Store.authenticate
  hashes it to an owner. This is local identity, NOT real login. All state is owner
  scoped. GET /api/profile, PUT /api/profile with expected_version; product-state
  routes export their implemented OPERATIONS in product_routes.py.
- POST /api/chat accepts message, expected_profile_version (null only unsaved),
  optional selected_role_ids/selected_skill_ids/previous_context_id. Response:
  answer, statements, provider, profile_version, context_version, action_status,
  behaviour_policy_version, integration_mode plus routing/diagnostics extensions.
  See docs/execution/product/llm/FRONTEND_CONTRACT.md. Current closed evidence
  selector cannot generate substantive roadmaps. Canned capabilities are not proof.
- SQLite Store documents have id/kind/version/data; exact versions and owner are
  server validated. D product migrations5/6 preserve legacy1–4. Actual visible
  transcripts are NOT stored yet. Mindbot's old redirect is superseded.
- Direct actions/proposals use the existing ActionExecutor. Direct POST
  /api/direct-action has typed request + idempotency_key; inferred proposals require
  explicit decision on exact immutable content. Never trust model-supplied authority.
- CV library exists with local private filesystem provider; normal A storage is
  disabled. Hosted durable bytes/DB/real login remain required, not accepted.
  F-DOC-REVIEW-R01 remains open: after uncertain review response, editing textarea
  diverges from cached exact retry body. F fixes UI; D retains exact-body replay
  protection and verifies CV/resume purpose/extraction/ownership.

## New interfaces — implementation agreement, not yet live endpoints

D owns conversations.py, conversation_schemas.py, identity_store.py, Store and
PostgreSQL adapter if hosting requires it. D exports implemented OPERATIONS and
dispatch(app,owner,method,path,body); A registers exact committed paths promptly.
Use /api/product/conversations (GET/POST Minder only), /api/product/conversation
(GET/DELETE by body conversation_id), /api/product/mindbot-conversation (GET creates
singleton atomically), /api/product/conversation-turn (POST). The turn body is
{conversation_id,message,idempotency_key,expected_profile_version}; channel is
server-read from the owned conversation, never supplied action authority.
Minder allows multiple chats; Mindbot exactly one per owner, no creation/deletion/
thread-switching endpoint. Messages are ordered visible user/assistant results.

D reserves begin_turn under a unique(owner,conversation,key); provider is invoked
outside a DB transaction; completed retries replay saved response without invoking
model or actions. Conflicting same key/body rejected. Pending/uncertain returns an
explicit state, never automatically reruns a mutation. D calls the A-owned callback
app.conversation_turn_handler(owner,channel,message,history,request_id,body) returning
validated visible response dict, then finalizes. History is bounded owner-scoped
visible content only; no credentials, raw CV or hidden reasoning. Failed provider
gets saved truthful result and manual new-turn retry. D owns atomic append of
scheduled notice/event keyed by existing event ID into the SAME Mindbot singleton.
D may export a smaller equivalent Python service first; commit exact contract before
F wires it. Do not claim planned route availability until OPERATIONS exists.

E owns auth_adapter.py: verify_identity(token,request_context=None) -> mapping
{issuer,subject} with optional safe display metadata, or AppError401/503.
Use maintained provider SDK, verified signatures/issuer/audience/expiry. Export
public_config() with public login fields only. A identity_boundary.py/common API
maps that verified identity through D identity_store.py, never trusts browser owner.
D maps issuer+subject to a fresh stable owner; never claims anonymous data. E must
publish precise config requirements and function signatures in its first handoff.
Hosted mode must fail closed without configured identity; anonymous local mode
remains explicit. A owns route registration and CSP/common runtime hooks.

A owns generation.py/generation_schemas.py/message_orchestrator.py and existing
chat/actions/agents/worker orchestration. Typed advice/roadmap/task drafts include
policy version, model, role/profile references, explicit assumptions, clarifying
questions and grounded fact references; generated advice is distinct from empirical
facts. Generation does not mutate plans/tasks. Existing plan/task APIs materialize
only explicit direct instructions or approved exact proposals. No model ranking,
forecast probabilities or invented competence. Backend scorer unchanged.
E hosted_worker.py wraps existing worker; D persists schedule/next/last/deduplication;
A defines permitted orchestration and appending results; F owns controls/display.
No competing scheduler. Publish exact implemented worker contract before hosting.

## Design authority and F assignment

- docs/minder-approved-product-designs/profile-v2/: approved self-contained HTML,
  design context, reference PNGs and source checks.
- docs/minder-approved-product-designs/explore-v1/: separate Careers Matches/Compare/
  Outlook and My Path Next steps/Roadmap/Skills/Progress; final references and logic.
- docs/minder-ui-html-previews/: previously approved Minder/Mindbot shell references.
- MANIFEST.json records imported exact hashes. Fixture users/ratings/illustrative
  rankings/localStorage identity are NOT live data or replacement scoring rules.
  Source-package framework suggestions do not authorize a framework migration.
F owns all apps/frontend-product/**, login/history/Mindbot chat/generated output,
CV retry and approved pages. No Explore deferral, no Mindbot-to-Minder redirect,
no New chat or thread switching in Mindbot. Preserve completed repair/accessibility.

## Hosting/access dependencies and handoff protocol

E inspects connected Replit first and selects actual existing target/resources.
Connected app Aiversecity Career Compass (d8e6ee62-0e31-4863-bf19-b457893d558c)
is a candidate requiring E verification, NOT a confirmed Minder deployment.
No Replit coding agent rewriting concurrent lane work. E and D choose actual durable
DB/private object bytes from verified account resources; PostgreSQL needed if chosen
host cannot guarantee SQLite durability. Current DATABASE_URL/host login/storage
configuration are unverified; do not invent access or introduce billing upgrades.
A owns root dependency additions requested by D/E. CV PDF text extraction may need
pypdf; no OCR scope. Pinned read-only raw/derived source inputs are not Git artifacts;
E must package only permitted pinned data and preserve provenance for hosted runtime.
Localhost is not a remote frontend backend. Publish actual HTTPS origin only after
hosted acceptance. No final login/history/CV/scheduler waiver.

Every handoff: full SHA, dependencies, owned changed paths, actual checks and gaps.
Producer commits/pushes its own branch normally; A inspects and merges only missing
committed changes. No copying active lane files, squash/rebase/force push. A verifies
remote snapshot SHA. Existing branch pushes authorized; no main merge/tag. Prepare
history-preserving release PR after tested candidate; judge deployment requested
within existing resources with E. Report local, hosted and forecasting status separately.
