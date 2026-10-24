# MA1-R02 — actual D integration and next persistence interfaces

Merged D bbe4e1b1e248fd41a1cc621ac9b30d1860622941; A registry includes ALL exported
conversation operations, including POST browser read alias. D callback consumes
A real generator and current channel history, actual response persisted. Auth owner
boundary now calls actual identity_store.owner_for_identity(store,VerifiedIdentity).
GET /api/auth/config and GET /api/auth/session from51e1848 are implemented; F can
wire both now. Neither public config nor signed software tokens prove real login.

A actions output adopts D allowed fields actions[],action_ids[],proposal_ids[],status
rather than unrecognized action_result/action_error. These are real executor results.
D persists response and exact retries, so reloading/retrying cannot rerun the action.
Worker now atomically calls D append_notice in the existing notice transaction;
construct Conversations before transaction to avoid nested SQLite writer locks.
Pause also pauses queued daily events; resume requeues; old missed-day backlog is
superseded so browser-closed restart catches up today once, not a replay storm.
E consumes app.scheduled_worker from build_hosted, not a second scheduler.

## D independent next slice agreement

D exclusively owns new automation_state.py/generation_state.py and tests, now named
in OWNERSHIP.json. Existing schemas/migrations/Store remain D only. No A file edits.

- save_automation_settings(store,owner,settings,expected) may extend canonical existing
  agent_settings with enabled,check_time,timezone,state(active|paused|cancelled),
  scope{plan_ids},next_run,last_result. Preserve explicit default Asia/Kuala_Lumpur;
  do not silently reset existing canonical settings. state/enable consistency:
  active=true, paused/cancelled=false. Scope is explicit, never all users.
  Validate owned plans, timezone/checktime and expected version. Reuse same existing
  agent_events/notices and event IDs. D exports exact implemented signatures/routes
  early; A delegates configure and pre/post worker checks after inspecting delivery.
  Worker handles one latest due check after downtime, pause/cancel suppress pending
  work, no completed action replay. next/last derive from actual persisted runs,
  never a browser-only scheduled timer. E loop drives existing worker only.
- Record generation typed draft and metadata using Store, preserving source
  profile/version, policy/model, role reference and accepted canonical plan ID.
  Exact generator schema and actual module: generation_schemas.SCHEMA; output
  generation={policy_version,draft_id,status:unsaved_draft,model,profile_version,
  advice:{kind,answer,assumptions,questions,stages[{title,outcome,tasks[{title,
  description,estimated_hours}]}],fact_ids,operation},claim_scope}.
  D can export record_generation(store,owner,generation) and acceptance wrapper
  consuming app.generation_materializer(owner,generation,role_id)->canonical plan
  draft. A owns materializer content/role reference validation; D persists via
  existing create_plan plus exact idempotent acceptance reference. Explicit accept
  body names generation draft, role, current profile revision and key. Stale source
  Profile requires regeneration/review, not silent promotion. No active plan change
  unless that explicit acceptance scope includes it. Keep one authoritative task
  graph; no duplicate localStorage graph or claimed mastery. D commits exact contract.

F should consume existing D conversations now, typed generated answer and phases;
no need to await full release. New broader operation tools/automation and generation
acceptance remain pending, not advertised as completed. Draft request alone saves
no plan. Current completed operation subset is task completion/reschedule with exact
user authority or reviewed proposal; no model weights/ranking policy replacement.

Materializer is now installed: app.generation_materializer(owner,generation,role_id)
returns canonical PlanProgress draft only, no DB write. D can implement acceptance
against this callback now. It requires current source Profile version, partial saved
Profile, supported eligible explicit role and validated guidance draft with stages.
Server creates deterministic opaque task IDs from owner/draft/role/positions for
stable retries; no fabricated skill/evidence/resource IDs. Tasks are proposed,
unscheduled, uncompleted, no mastery, with each stage depending on the previous
stage's tasks. Generated effort stays a proposed estimate. Existing create_plan
assigns actual canonical plan ID/version; D retains provenance/acceptance reference.
No implicit active direction change. Save/activate are separate explicit scopes.
