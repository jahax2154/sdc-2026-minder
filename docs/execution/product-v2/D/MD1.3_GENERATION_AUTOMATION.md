# MD1.3 — versioned generated/accepted plans and canonical daily state

Service slice, schema7 unchanged. Reuses Store.documents/history, existing
create_plan/plan_design, product_requests, agent_settings/agent_events/notices.
No second plan graph, queue, scheduler or database. A owns generation/materializer,
tool authority, routes and Worker execution; E drives that same Worker.

## Generation export

Internal record_generation(store,owner,generation) accepts A's validated typed output
(generation_schemas.SCHEMA advice, policy/model/source profile/draft ID metadata).
It persists one immutable draft, status generated, actual version, accepted_plan_id
and accepted_state_version initially null. Repeat same draft/content returns same
record; changed same-ID content409. Source profile revision must belong to this
owner (historical same-owner versions allowed for review, never foreign versions).
Generated advice is NOT an accepted task graph and creates no plan/skills/direction.

Proposed A registration from generation_state.OPERATIONS:
GET /api/product/generations -> {generations:[stored draft records]};
POST /api/product/generation {draft_id} -> {generation:record};
POST /api/product/generation-accept using generation_state.ACCEPT_SCHEMA:
{draft_id,role_id,expected_profile_version,expected_generation_version,idempotency_key}.
No raw generated advice/model/assistant payload accepted from clients.

Acceptance calls A app.generation_materializer(owner,generation,role_id) outside
transactions, then rechecks source/actual Profile and generated version inside the
write. Existing create_plan now supports optional internal db for atomic metadata
link; creates canonical PlanProgress once and versioned provenance design. New tasks
must be proposed/unscheduled, uncompleted/unlocked and never mastery-verified.
Current profile change requires regenerate/review409, not silent old-plan promotion.
Response {generation:accepted record,plan,feasibility,activated:false,
requires_explicit_direction_selection:true}. Selection remains separate explicit
PUT direction. Eight concurrent identical acceptances create one plan/reference;
exact old retry returns cached original result, so consumers refetch current state.
Generated->accepted versions remain in existing history. Accepted plan later edits
use canonical PlanProgress/history, not copies of generation output.

A must call record_generation after successful real model validation and expose the
stored generation version to F. D does not claim a fixture draft is real generation.
Before route registration/materializer/hook integration, operation is not live.
A04e16e9 materializer is available; nonempty fact_ids need applicable factual
revalidation in A rather than passing empty fact sets or dropping citations.

## Automation export

save_automation_settings(store,owner,settings,expected,at=None) persists the SAME
agent_settings record. Client settings fields: enabled?,check_time(HH:MM)?,timezone?,
state(active|paused|cancelled)?,scope:{plan_ids:owned unique IDs<=20}?. New defaults:
09:00,Asia/Kuala_Lumpur,active,all own plans (empty plan_ids). Empty scope means this
user's plans only, never other users or autonomous edits. Omitted edits preserve
saved values. Enabled/state must agree. Explicit scope references must be owned.
Server computes next_run (UTC) and preserves last_result. Paused/cancelled -> null
next_run/enabled false. No browser can supply next_run,last_result or edit authority.

Pause/cancel removes leases and suppresses queued/processing daily events so an
in-flight analysis cannot later commit an unapproved result. Resume requeues only
this local day's paused/cancelled event; older backlog stays cancelled. Changing
time/timezone/scope cancels outstanding old-scope daily events. Completed events/
notices/history remain intact. No new worker is created; A must delegate configure
and respect these fields, due time/timezone, scope and cancellation in its Worker.

record_automation_result(store,owner,event_id,db=None,at=None) reads an actual
persisted daily event, attaches last_result{event_id,status,observed_at,notice_id?,
conversation_id?,message_id?}, computes next_run and appends any actual saved notice
once through existing singleton bridge. Repeated same event/status does not bump
settings version or duplicate a message. It can run inside A's completion transaction.
No invented run success or browser timer. E startup reconciliation appends existing
notices without rerunning jobs. Clock/date logic uses the saved IANA timezone.

## Verification / integration dependencies

9 focused generation/automation/existing-plan tests pass: immutable/versioned draft,
concurrent acceptance, one canonical graph, no auto activation/mastery, stale source,
foreign drafts/references, failed materialization, scoped timezone schedule,
pause/lease invalidation/resume/cancel, stale settings, existing run ref and one
singleton message, invalid schedule/scope and UTC/local date boundary.
Fixtures are explicitly software generation/materialization; A owns real model
acceptance. A/E must run the existing Worker integration for actual due/catch-up/
cancellation, and hosted proof remains blocked on the selected volume/login access.

Integrated suite127 discovered:123 passed/4 Clerk SDK skips on legacy3.9;
pypdf support tests enabled. No real-provider or hosted claim follows fixture tests.
