# Optional fourth session D — personal-agent orchestration and scheduler

DO NOT start this task merely because the file exists. It is enabled only when the user chooses a fourth Codex session, C has committed provider/action-service contracts, and A has assigned a distinct worktree/branch and non-overlapping paths. In the default three-session setup, C implements this work.

Read the canonical revision-5 context, handbook and current ownership manifest. Confirm the exact C foundation SHA, domain-tool schemas, auth/approval records and test fixtures are present. If not, return the precise handoff missing; do not create a second provider or action executor. Do not change C-owned schemas to unblock yourself.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| D1.1 | Consume C provider/action interfaces and add event orchestration | Bounded worker/event checkpoint |
| D1.2 | Daily scheduling, notices and approved-action workflow | Scheduler/authority checkpoint |
| D1.3 | Verify retries, stale state and integration; hand off | Culminating D checkpoint with truthful live-versus-local status |

## Own

- Agent decision/orchestration layer consuming C's Groq adapter and domain tools.
- Durable event handling, relevance checks and notification planning.
- Daily scheduler/worker integration and bounded retries.
- Agent-specific tests/reports in the assigned paths.

## Do not own

- API routes/router registration, database migrations, user authentication, plan/profile write implementation, provider credentials/adapter, company retrieval or frontend pages.
- A/B numerical models, source taxonomy, model selection or root dependency locks.

Request changes from the owner through a small committed interface/change request. A integrates; do not cherry-pick arbitrary unreviewed work or run concurrent migrations.

## Implement

1. Consume material market events with source/version metadata and user role/industry/skill relevance. Suppress duplicate/redundant notices. Missing evidence does not become a demand spike.
2. Daily local-time check loads current tasks, completed work, availability, locks and deadlines. Generate a concrete feasible rescheduling proposal; do not mutate automatically from the check.
3. Task-completed events trigger next-step/reflection suggestions while preserving skill-evidence distinctions. Time/constraint/preference changes trigger analysis/proposals based on explicit updated state or staged context.
4. Use one bounded LLM tool workflow with typed proposals and explicit result status. Neither the LLM nor a retrieved page can invent approval authority.
5. Direct, sufficiently specific user requests can call C's executor with the real authorising request ID. Proactive/inferred changes must create a pending proposal. Approval applies only after C verifies the user and approved diff/state version. A statement of overwhelm or hypothetical career interest cannot become a direct command.
6. Preserve complete state transitions: received, analysing, proposal-ready, awaiting-approval, applied/rejected/failed. Use existing equivalent states where present. Prevent duplicate jobs/mutations on retries and preserve before/after audit records through C services.
7. Deliver in-app notices only; no unsolicited external messaging tools. Actual writes are reported as successful only after executor confirmation. Support configured scheduler timezone/check time and missed-job recovery with bounded cost.

## Verify and return

Exercise event deduplication, relevant-source notice, no mutation before approval, direct instruction without redundant approval, ambiguous intent clarification, rejection, stale state, failed writes, unavailable forecast and worker restart/retry. Use shared fixtures first, then real C tools in integration. Mocked scheduler tests do not establish live scheduled execution.

Return commit SHAs, worker/start/schedule configuration, event subscriptions, required C registrations, tests and actual integration evidence. You do not independently deploy or spend on RunPod. C/A integrate your worker through the declared interface and verify deployment. Continue until this assigned implementation is complete or a specific external dependency remains.
