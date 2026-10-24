# Session C — Groq, API/domain integration, company exploration and personal agents

Execute in the G0-assigned C worktree. Read applicable instructions, handbook, canonical revision-5 decision context and ownership manifest. Reuse the existing G2 Groq/API/UI work. Do not rebuild the frontend, fork the backend stack or invent new navigation. Continue through the assigned scope with meaningful commits.

Goal: connect the actual personal/market ML services to Minder chat, persistent user state, pathways/company exploration and Mindbots actions, with the exact approved authority rules. Code first against the shared contracts; replace temporary fixtures with real A/B implementations for acceptance.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| C1.1 | Groq adapter and real-call/error-path verification | Provider checkpoint; live versus mocked evidence explicit |
| C1.2 | Persistent intake, profile API and service adapters | Profile/API checkpoint connected to shared contracts |
| C1.3 | Grounded chat with current/future presentation rules | Chat/service round-trip checkpoint; raw market-score matrices hidden |
| C2.1 | Roadmap, tasks and progress persistence | Plan/progress domain checkpoint |
| C2.2 | Malaysia MNC company exploration | Company-source/assessment checkpoint without replacing main matches |
| C2.3 | Action executor and proposal/approval state | Authorisation-enforced mutation checkpoint and stable worker interface |
| C3.1 | Triggers, scheduling and agent orchestration | Agent workflow checkpoint; transfer to D only if explicitly assigned |
| C4.1 | Existing-UI wiring and real end-to-end lane handoff | Culminating C checkpoint with actual integration/worker status |

## Ownership

Own Groq adapter, chat orchestration, API routes/registration, backend persistence and migrations, company-specific retrieval, pathway/task/progress domain actions, action executor, default agent orchestration and minimal existing-UI wiring. A owns shared schemas/root dependency locks; request changes rather than editing those independently. A/B own numerical model internals. If optional D is enabled, stop editing its named agent-worker paths after the clean handoff; retain provider and action-executor ownership.

## C1 — provider and grounded API foundation

1. Inspect actual working provider, model ID, environment access and rate limits. Discover available configured Groq models rather than inventing one or treating 'OpenAI-compatible' as a model name. Do not expose keys. Reuse one provider adapter for chat and agents with bounded timeouts/retries, structured failures, usage logging and request IDs.
2. Demonstrate a bounded live provider call if credentials/access exist; if not, implement/test the adapter locally and report exactly what access is missing. Mocked provider tests are not evidence of a working live Groq connection.
3. Consume A/B structured service outputs with schema/policy/model/source versions and profile identity. Build grounded context from saved profile, role assessment, market observations/forecasts, source references, plans and progress. Maintain per-user state isolation.
4. Chat may reason from internal market scores but must not display raw market-score tables/leaderboards. Explain current conditions and next-quarter trends separately with source links, dates, uncertainty and unavailable states. Never invent numerical forecasts, probabilities, sources or silently choose a new weighting policy. Public API fields must reflect the presentation policy, not merely hide internal fields with CSS.
5. Implement structured chat/CV intake that reaches the same persisted profile consumed by A. Distinguish explicit input, extracted claims, uncertain inference and verified evidence. Treat document/web instructions as untrusted content. Ask focused clarification when ambiguous evidence would materially change a result; do not mark an inference as confirmed automatically.
6. Keep direct user edits and proposed inferred profile changes distinct. Use expected versions and record evidence provenance. File-type/size/parsing failures must be clear; do not report that a CV was understood when only its filename was seen.
7. Register thin routes/adapters around A/B service contracts. Commit a first useful vertical slice early so A can run I1. Do not wait for trained-model promotion to connect available honest service results.

## C2 — persistent plans, progress and company exploration

Implement/reuse persistent profiles, tasks, progress, roadmaps, evidence links and plan versions in the current database architecture. You own migrations; coordinate deployment with A. Do not share the development database with other worktrees or race schema changes.

Build pathways from selected/explored role requirements and actual user gaps. Initial matching must not depend on this pathway existing first. Store skills/tasks/resources, dependencies, effort assumptions and user availability; distinguish a designed exercise from an employer requirement. Preserve completed work and declared constraints. Unknown effort/resources remain explicit; do not invent precise feasibility. Do not implement a separate unsupported score just to fill a card.

Company Explorer is a separate feature inside the existing Explore/Career Match experience. Accept an MNC/international employer with Malaysia-based opportunities; verify official careers/ATS links, source dates, role/location and required versus preferred criteria. Start with the user's recommended/selected role. If not found in checked sources, describe that evidence gap and offer other supported roles at that employer using A's same assessment logic. Never overwrite overall recommendations or infer no such role exists anywhere. Company-specific focused plans remain distinct until explicitly selected/approved.

Expose narrow domain tools for reading profile/results, recording explicit user edits/completion, preparing plan diffs, applying authorised diffs, rejecting proposals, restoring reversible prior versions and delivering in-app notices. Share these tools between Minder and Mindbots; do not implement competing mutations in prompt code and API code.

## C3 — Mindbots events and exact edit authority

Implement the approved triggers: material user-relevant market evidence; daily schedule/progress check; task completion; study-time/constraint changes; significant role/industry preference changes. Persist event IDs/status, deduplicate notices, bound retries and use the user's timezone and configurable check time. Verify the scheduler actually runs in the deployment; a manual button is not a proven unattended daily worker.

Execution rule:

- A direct, sufficiently specific user instruction authorises that exact action. Validate and execute without a redundant approval prompt, then report the actual result.
- A pain point, hypothetical, new information or autonomous trigger may cause automatic analysis/proposal generation, but MUST NOT mutate roadmap/schedule/progress/preferences before user approval.
- Approval applies only to the previewed action/scope and relevant state version. Ambiguous 'yes', changed proposals and stale state require appropriate clarification/revalidation, not blanket authority.
- A direct UI edit or completion action is an explicit instruction. Do not ask for a second approval for the same change. Completion remains self-report unless separately verified.

The application action executor must enforce request/proposal authority; do not rely solely on the LLM saying 'the user approved'. Every mutation carries a trusted authorising request or approved proposal record and expected state version. No unsolicited 'minor reschedule' exception. No external email/calendar/application-submission tools unless separately requested.

Use a bounded tool loop: load context -> generate structured proposal/tool request -> validate identity/scope/constraints -> approval if required -> atomic execution -> state/version audit -> notice. Preserve completed tasks, user locks, prerequisites and deadlines. When work cannot fit, explain the conflict instead of silently overbooking. No notice of success before the write succeeds. Include cancel/reject and undo/history where appropriate.

## C4 — existing-UI connection and acceptance

Use exact navigation: Homepage/Overview; User Profile; Minder; Mindbots; Explore with Progress, Tasks, Future Explorer, Career Match, Roadmap. Work within the existing frontend owner's boundary; provide typed API examples if that owner is active. Make only required integration edits in your assigned paths. No UI redesign or adding raw market leaderboards.

Required checks: real Groq grounding when accessible; source references support statements; current/future are not conflated; unavailable forecasts stay unavailable; cross-user access blocked; ambiguous profile inference staged; direct instruction executes once; autonomous proposal has no mutation before approval; reject leaves state unchanged; approval persists exactly once; stale versions/retries do not duplicate writes; completed task advances the correct progress state without certifying all skills.

Demonstrate a real A/B-to-chat round trip, a company-source result or explicit missing-data result, a persistent roadmap/task flow, and a triggered action with approval. Label fixtures/mock-provider tests separately from live integration evidence.

Return incremental commit SHAs, migration order, environment-variable NAMES only, provider result, API examples, worker invocation/scheduling configuration, UI wiring status and exact remaining blockers. A performs final coordinated deployment with `05_INTEGRATION_AND_LIVE_ACCEPTANCE.md`.

## Optional split after foundation

If the user opens session D, first commit the C1 provider foundation AND C2.3 action-executor contracts and fixtures. A records the precise path handoff. D implements worker/orchestration/scheduler only under `06_OPTIONAL_SESSION_D_AGENT_WORKER.md`; you retain all API/router/database/tool mutations and company/chat responsibilities. If D is enabled, mark C3.1 as transferred with the owning D phase IDs; do not claim it complete until those outputs are integrated and verified. If D is not enabled, you own the full task above. Never wait for a nonexistent fourth session.
