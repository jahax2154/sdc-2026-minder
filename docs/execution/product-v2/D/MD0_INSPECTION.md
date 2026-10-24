# MD0 — Revision3 persistence reconciliation

Read the original docs/Minder_Morning_Completion_Runbook_2026-10-24.md,
Revision3 (24 October2026). This audit preserves D9f1f2ee and precedes dependent
edits until A publishes the current immutable M0 ownership/base. It does not claim
hosted persistence or completed conversation storage.

Actual local observation: Python runtime SQLite3.51.0; Store uses per-request
SQLite connections, WAL and BEGIN IMMEDIATE writes. Reserved D runtime DB exists,
migrations1–5, zero canonical documents. Migration6 library service exists in code
and is tested, but has not been activated against this reserved DB. Storage mode
disabled; no DATABASE_URL configured. No PostgreSQL client/server/driver or PDF
text parser installed in this environment. No private state or credentials printed.
Unrelated raw/derived source folders remain untouched and untracked.

The preserved D baseline73 backend tests passed. Existing source implements
canonical Store.documents/history, profile/plans/tasks and versioned state writes,
agent_settings, agent_events and notices. Reuse those records. Visible transcript
persistence, external identity mapping, hosted database/storage and CV-purpose
validation are missing. Do not create another task/plan/schedule database.

A's integrated1285670 contains completed chat/frontend repairs but still explicitly
lists temporary visible conversation and deferred F-DOC-REVIEW-R01. That defect is
the editable frontend textarea diverging from a frozen uncertain correction body;
backend request/body idempotency already behaves correctly. A/F were informed;
D will verify no repeated profile write, not edit frontend files.

## Proposed service boundaries for A/E/F review (not yet implemented)

A owns public HTTP schemas/routes and model/action orchestration. D exports only
persistence services after M0 grants exact files. E supplies SDK-verified identity
and selected hosted storage/runtime. Target choice is pending actual access; a URL
cannot convert SQLite. No parallel hosted implementation is being started.

- Verified issuer+subject maps atomically to a newly allocated application owner.
  No anonymous/local owner is adopted by first login. Never accept browser owner IDs.
- Multiple Minder conversations, owner-scoped create/list/open/delete/continue.
  Mindbot has atomic get-or-create with database uniqueness and no new/list/delete
  or thread-switch path. Concurrent first visits return the same identity.
- Turn acceptance stores one user message and a request scope. Provider callback
  executes after the write transaction closes. Finalization stores server-visible
  assistant outcome/source/action/proposal references; client cannot author them.
- Exact retry reads the saved turn/outcome and cannot re-execute provider/actions.
  Interrupted/uncertain action outcomes remain explicit, not auto-replayed. History
  reads do not execute tools. Context passed to A is bounded and channel-scoped.
- Existing canonical PlanProgress/history persists generated/accepted plan state;
  generation provenance is metadata referencing those versions, not a second graph.
- Existing agent_events/notices remain schedule execution authority. A/E call an
  idempotent D notice-to-history append hook so each scheduled result appears once
  in the same singleton Mindbot. No duplicate scheduler/job database.
- Preserve private document storage; new uploads explicitly declare CV/resume
  purpose and use supported extraction/review only. Legacy files stay unclassified
  until explicit review. No extension-only claim that purpose is verified.

Next dependency: exact committed A M0 base/ownership/routes/callback contract;
E verified engine/storage/identity interface. Independent baseline audit is complete.
