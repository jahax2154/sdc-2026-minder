# G0 — recover current work, freeze interfaces and launch three lanes

Execute this task in the actual Minder repository. You are session A and the integration owner. Read `00_EXECUTION_HANDBOOK.md` and the canonical `MINDER_AI_ML_DECISION_CONTEXT.md` (content revision 5). This is executable work, not a request for another general plan. Do not rebuild the monorepo.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| G0.1 | Inspect, preserve and checkpoint current repository work | Truthful local recovery commit; current-state evidence |
| G0.2 | Freeze ownership, shared interfaces and numerical-policy mapping | Shared contract/config/fixture commit; unresolved decisions isolated |
| G0.3 | Create/reuse isolated worktrees and publish launch instructions | Culminating bootstrap checkpoint; every lane has the launch/contract commit |

## 1. Inspect and protect the actual state

Read applicable AGENTS.md, existing stack/runtime configuration, policy documents, current reports/evidence, relevant code, source manifests, git status/log/worktrees/remotes, and current running-session ownership. Reuse prior context exports if still current; verify changed facts.

Identify the existing personal fit, market, learner, Groq, agent, persistence and API paths. Record what works, not just filenames. Do not assume FastAPI/React layouts or that a model artifact is active because training code exists.

Preserve local work and inspect staged/untracked content. Coordinate if another session is writing the same files. Create truthful, focused recovery commits of understood project work; do not discard unrelated edits or include credentials, private user records or large reproducible artifacts. If earlier checkpoints never existed, document that current recovery is today's state, not reconstructed history. Do not backdate. Do not push or remotely back up Git branches now. Wait for an explicit user push instruction, then verify the intended remote and scope. Do not invent a remote or force push.

Canonical context integration: place/update the one decision file in the project's appropriate docs location. Record it in existing agent instructions by reference instead of duplicating all rules in AGENTS.md and replit.md. Preserve other technical policies; mark conflicting product instructions superseded in the decision index, not deleted blindly.

## 2. Prepare concrete ownership and numerical mapping

Create a small execution manifest in the existing reports/docs area with actual repository paths for A/B/C ownership, shared-file owners, report/artifact directories, worktree branches, contract version, local ports/database isolation and integration branch. A owns shared schemas/root locks; C owns backend migrations and router wiring; B owns paid RunPod execution. Do not leave overlapping ownership implicit.

Audit current numerical definitions against the new role-fit meaning. Record factors/units/ranges, sources, missingness, preference treatment, market compatibility, and each reused versus changed formula. Preserve the user's industry-assessment stage and remove automatic industry-threshold exclusion. Detailed learning milestones cannot remain a prerequisite for initial matching.

A complete numeric policy is not present merely because prose decisions are settled. Reuse compatible approved values; propose and version concrete replacements for changed meanings. Do not silently reuse old milestone-preparation labels or train Ridge on targets with a different meaning. Do not invent a current/future blend or let the LLM choose weights per response. If a substantive scoring choice has no authorised basis, return ONE concrete proposed diff/example plus the affected output; implement the independent parts and keep that policy version explicitly pending. No blanket stop for unrelated work.

## 3. Commit shared interfaces and useful fixtures

Adapt existing contracts rather than creating a parallel API system. Define fields, units, IDs, versioning and missing states for:

1. Profile evidence, preferences, current fields, constraints and their provenance.
2. Occupational role IDs and many-to-many industry/skill mappings.
3. Personal assessment: score status, components, industry contribution, gaps, prerequisites and trace.
4. Market results: current versus forecast kind, Malaysia scope, source universe, observation/issue/target dates, next calendar quarter, count units, uncertainties, missing reasons and source IDs.
5. Recommendation result: profile/policy/model versions, candidate IDs, personalised ranking and explicit market-period policy key; separate internal scores from public response fields. No hidden current/future average.
6. Company-role result: employer/location, official evidence, matching/unknown requirements, searched scope and no-role-found semantics.
7. Plan/task/progress and proposal/approval/execution result, including expected state version and authorising request/proposal ID.

Define callable A/B service boundaries and C adapters, with no dependency on another worktree's absolute path. Supply small clearly synthetic contract fixtures for complete, partial, unavailable forecast, no-company-role-found, not-interested, direct action and approval-required cases. Fixtures are temporary integration inputs, not data-readiness or empirical-quality evidence.

Commit minimal interface code and fixture validation. Do not spend the setup phase implementing all business logic. Database schema changes are C-owned; shared type definitions are A-owned.

## 4. Create worktrees from the verified checkpoint/contract commit

Inspect existing worktrees/branches first and reuse safe ones where appropriate. Create three distinct working directories on separate branches from the same committed contract base. A's integration/personal branch, B's market branch and C's app branch must be explicit. Do not create worktrees from stale HEAD that omit required uncommitted work. Do not clobber an existing directory/branch or copy an entire dirty checkout to simulate isolation.

Ensure all three see the canonical context and task pack. Configure independent temporary databases and ports where needed. Credentials remain environment-managed; worktrees need access configured without committing secrets. Identify read-only shared raw data and separately owned generated outputs; one writer per artifact path.

## 5. Return an actionable launch report

Print a three-row table: session, exact directory, branch, prompt filename. Include checkpoint/contract commit SHAs, canonical context path, ownership manifest path, which components already work, actual missing access, and any single unresolved substantive policy proposal. Say exactly whether G0 is ready and why.

G0 passes only when the launch information and shared interfaces exist and the sessions can work without overlapping writes. It does not require all datasets/labels/training to be finished. Missing data must be routed to the responsible lane, not converted into another setup-only gate.

Before launching B/C, fast-forward their clean new worktrees to the final G0.3 launch/contract commit so the ownership manifest is present in each. Do not assume a worktree created before G0.3 automatically receives it.

After returning launch details, session A can continue with `02_SESSION_A_PERSONAL_MATCHING.md`. Sessions B and C run their respective prompts in the printed directories. Do not launch duplicate processes if the user already started those sessions.
