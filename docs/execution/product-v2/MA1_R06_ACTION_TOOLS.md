# MA1-R06 — typed conversational task/profile tools

Extends the existing shared ActionExecutor/authority/idempotency/audit rather than
creating a second tool writer. A generation operation schema now includes create_task,
edit_task,schedule_task,update_preference,change_goal (automation awaits D delivery).
The real model interprets request/payload/owned target; backend validates and executes.
Provider cannot invent expected versions, mastery/evidence/resource IDs or authority.

Server scope: exact entire current message quotation plus explicit instruction
framing (including polite 'Could you please…'); suggestions/conditional/pasted examples
produce immutable proposals, never direct writes. More than one task with no specific
ID/title asks for target. Unknown time asks instead of guessing. Exact zoned ISO or
explicit today/tomorrow+clock resolves deterministically in saved timezone; 'tomorrow
evening' remains missing time. Model-generated dates are not blindly trusted.

New task starts proposed/unscheduled/uncompleted with no mastery or invented links.
Edits preserve locked/completed tasks. Scheduling still requires known effort/capacity
and existing feasibility constraints. Goal edits change user-reported context only.
Preference updates/reset use existing one-state semantics and leave skill evidence
untouched. Conversational execution keys now hash conversation+client key so two
threads cannot collide merely by reusing a local request key. D reserves/replays turns;
no automatic write retries. Result carries actual actions/action_ids or proposal_ids.
Unscoped create/schedule cannot be undone by a guessed generic inverse; use explicit
canonical task controls. Existing approved legacy actions/proposals remain compatible.

Shared ActionDiff accepts a typed Task only for new activity creation; arbitrary
objects remain disallowed and executor enforces path/kind/flags/scope before any write.
No scoring formula or empirical evidence treatment changes. Generation estimates are
proposed pathway effort, not assessed competence or claimed user time capacity.

19 focused software checks pass: legacy actions + typed generation/orchestration,
create/edit canonical tasks, preference/reset preservation, goal change, exact replay,
partial profile guidance, ambiguity/missing time, direct versus proposed authority.
These action selections use declared model spies; real paraphrase/action/provider
acceptance remains required on integrated runtime. Current real Qwen guidance and F
actual completion evidence are tracked separately. Full automation/cancel and explicit
roadmap acceptance follow D's committed state exports, not fabricated capability.
