# Minder — AI/ML parallel execution handbook

Prepared: 22 October 2026, Asia/Kuala_Lumpur. Execution-pack revision: 2.
Scope: complete the AI/ML services, Groq integration, personal-agent workflows and their connections to the existing application. Reuse the repository; do not restart the app or redesign its navigation. Product target: live before 23 October 23:59 MYT, equivalent to midnight starting 24 October. Longer-term one/five-year forecasts are not tonight's implementation scope.

## Checkpoints are mandatory

Read `07_PHASE_CHECKPOINT_RULES.md` first. Every execution prompt now includes bounded phase IDs and an explicit local commit requirement. The loop is implement -> verify -> refine -> record -> commit -> continue. Post-checkpoint repairs stay linked to the original phase as R01, R02, and so on. Each lane and the final integration also produce a culminating checkpoint. No GitHub/remote push is authorised until the user explicitly requests it.

Human-dependent work is deferred with a concrete decision entry; independent phases continue. Deferred and partially working phases are not passed gates. This applies even when the broader task is a long autonomous run.

## Start here

1. Put this pack in the project, preferably under the existing execution-docs area. Keep ONE canonical `MINDER_AI_ML_DECISION_CONTEXT.md`; the included copy is the revision-5 export of that file, not a second policy to maintain.
2. In the current project Codex session, run `01_BOOTSTRAP_CONTRACTS_AND_WORKTREES.md`. This session is A and owns integration. It inspects current work, recovers truthful checkpoints, maps owned paths, commits shared interfaces and creates isolated worktrees. Do not manually guess branch names or copy uncommitted source trees.
3. Bootstrap returns a launch table with exact working directories, branches and shared contract SHA. Open a terminal in each printed directory. Opening three terminals in the same directory is NOT isolation.
4. Give session A `02_SESSION_A_PERSONAL_MATCHING.md`, session B `03_SESSION_B_MARKET_FORECASTING.md`, and session C `04_SESSION_C_LLM_APP_AND_AGENTS.md`. Each prompt instructs Codex to commit after each listed phase and continue through eligible work without a routine permission pause.
5. Integrate the first working slices early. Once lane handoffs are ready, run `05_INTEGRATION_AND_LIVE_ACCEPTANCE.md` in A. Do not wait until every model experiment finishes to connect the real APIs.
6. Use `06_OPTIONAL_SESSION_D_AGENT_WORKER.md` only if you intentionally open a fourth session AFTER the C action/provider contract is committed and A records the ownership transfer. It is not part of the initial three-session requirement.

## Recommended three sessions

| Session | Owns | Must not independently change |
| --- | --- | --- |
| A — personal ML + integration owner | Occupational catalogue; industry affinity; profile-to-role features and fit; personal-fit learners/evaluation; shared contract and dependency coordination; final integration/deployment | B market internals; C API/domain implementations while their owner is editing |
| B — market ML | Malaysia evidence ingestion; credible news signals; current internal assessments; next-quarter role/skill forecasts; chronological evaluation; RunPod job execution | A fit formula or catalogue IDs; C API/router/database files |
| C — Groq + application/agent layer | Provider adapter; grounded chat; CV/chat profile intake wiring; API routes; persistent profiles/plans/tasks/progress; company exploration; action executor; agent triggers/approvals; integration with existing UI | A/B model internals; shared contract or root lockfiles without A coordination |

Two ML sessions are useful because personal suitability and market demand have different data, labels and evaluation. Do not split them into 'Ridge session' and 'XGBoost session': that would duplicate data preparation and create competing training/registry changes.

The latest schema, source taxonomy IDs and service contracts are shared; implementations and per-lane reports/artifacts are separately owned. Every lane receives the same canonical policy. Cross-worktree runtime files are not automatically shared. Use committed APIs/fixtures early and mergeable implementation commits, not imports from another session's absolute directory.

## Gates and actual outputs

| Gate | Owner | Required output | Runs alongside |
| --- | --- | --- | --- |
| G0 — launch readiness | A | Verified current state, checkpoint, exact ownership/paths, shared contract commit, launch table | B/C may inspect independently before launch, but do not mutate overlapping files |
| A1 — personal service | A | Broad eligible catalogue actually loaded; industry assessment retained; profile-to-role results and preference feedback traces | B1 and C1 |
| B1 — market service | B | Working real sources, provenance and current evidence; explicit data coverage; callable current/forecast interfaces | A1 and C1 |
| C1 — app/provider foundation | C | Real Groq call, grounded context, API adapters and persistent profile/task/action services | A1/B1 |
| I1 — first integration slice | A integrates, C wires | Profile -> real recommendation -> grounded chat; no fabricated market data; a real API contract round trip | Training/data enrichment continue |
| A2 — personal learners | A | Baseline/Ridge/boosting implemented and genuinely run where targets exist; separate policy/provisional vs independent evaluation claims | B2/C2 |
| B2 — forecasting learners | B | Next-quarter role AND skill forecast experiments/backtests where supported; otherwise truthful unavailable series; source/model evidence | A2/C2 |
| C2 — plans/company/agents | C, or split C + optional D | Persisted roadmap/task flows, company exploration, triggers, approvals and direct-request actions | A2/B2 |
| I2 — acceptance and deployment | A integrates; owners repair their modules | Integrated API/UI checks, deployed smoke evidence, model/source reports, truthful commits, exact remaining limitations | No concurrent edits to the same integration files |

Gates are acceptance checks, not new user-permission rounds. Continue within the approved task. A gate cannot pass merely because validators exist or tests run: the required service outputs must be demonstrated. A successful unavailable-state path does not mean a forecast was trained successfully.

## Shared contract and numerical decisions

G0 freezes data types and interfaces, not fabricated source facts or invented model quality. Required interface families: canonical profile/evidence/preferences; role reference; personal assessment; current market evidence; next-quarter forecast; recommendation result; source provenance; company-role assessment; plan/progress/task state; action proposal/approval/execution.

Current/future internal market scores must remain separate, and raw market matrices/leaderboards must not leak into normal UI/chat. Users receive explanations, source links and meaningful trend views. Personal-fit outputs are a separate presentation decision and must not be removed by accident.

The decision context does not settle every coefficient or a new current/future weighting. A owns one numerical specification derived from actual approved policies. Keep compatible existing values; version changed meanings. Routine technical mappings/configuration can be decided and documented by Codex. A genuinely new product-level score meaning or current/future blend must be a concrete, narrow proposal, not silently adopted. Continue independent work while that one dependent decision is unresolved. Do not repeat the full D01–D09 discussion or make routine constants a per-record approval queue.

## Ownership, handoffs and merges

- A creates a concrete path manifest; descriptive owners in this pack are not guessed filesystem paths.
- A owns root dependency/lockfile edits and shared schemas. C is the sole owner of backend migrations/router registration during lane development. A coordinates integration-time edits after the relevant owner checkpoint.
- B owns RunPod execution and a single budget ledger, including jobs requested by A. A prepares its personal-ML training job manifest/runner; B executes the immutable job and returns the artifact/provenance. No duplicate paid jobs.
- Each session uses its own dev database/schema, ports and artifact/output namespace. Sharing a Git repo does not isolate a live database or GPU account.
- Keep lane requests and reports in lane-owned paths. A publishes shared coordination changes; other lanes do not race on a single shared status file.
- Commits carry finished increments and real timestamps. A merges branches preserving their meaningful commits; no fabricated historical sequence, force pushes or blanket `git add .` over other people's changes.
- Existing G1A/G1A-R/G2 work is valuable input. Adapt it; do not redo functioning parts for a new naming scheme. Historical 'no commit' task wording is superseded by the architect's checkpoint instruction for this workflow.

## Practical cadence

Aim to finish G0 in one bounded setup pass, roughly 30–45 minutes if the repo is accessible; this is a planning target, not permission to skip recovery or guess contracts. Start with a thin working service slice before broad optimisation. Reserve at least the last quarter of tonight's available time for integration and repairs. Do not consume the whole window on model tuning or inaccessible sources.

At every listed phase checkpoint report: commit SHA, what now runs, actual coverage, tests/evidence, remaining blockers, and the next action. Do not stop merely to ask whether to continue. If blocked on one data/access dependency, complete independent implementation and return the exact unavailable input plus the prepared resolution. Do not spin on repeated requests to an inaccessible source.

## Optional fourth session: when LLM work can split

Initially keep C together: the provider, tool contracts and persistent action executor are shared foundations. After both the C1 provider foundation and C2.3 action executor are committed, optional D can own ONLY agent orchestration, event workers, scheduler and agent-specific tests. C retains provider/chat, company research, API endpoints and database/action execution. A updates the ownership manifest first. C stops editing D's assigned files. D does not create a second Groq adapter, competing migration set or duplicate scheduler.

More sessions before those boundaries exist create coordination work rather than useful parallelism. Three is the recommended launch configuration.

## Completion and reporting

Use separate columns for implementation, usable coverage, training run, evaluation and live activation. No single 'all passed' claim can conceal absent personal-fit labels, no Malaysian history, untested Groq credentials or a sleeping scheduler. The approved forecast-unavailable state is valid product behaviour; it is not successful empirical forecasting.

If deployment requires a GitHub push, stop only that release action at the prepared checkpoint and report it as awaiting the explicit push instruction. Do not push merely to meet the deadline.

The repository, access credentials and actual acquired datasets were not available when this pack was authored. These prompts therefore inspect and reuse real paths and facts at execution time. They do not claim tonight's work is guaranteed to finish regardless of access/data availability.

References: https://git-scm.com/docs/git-worktree ; https://console.groq.com/docs/tool-use/local-tool-calling
