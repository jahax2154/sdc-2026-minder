# Session A — occupational catalogue, personal matching and personal-ML experiments

You are session A in the exact worktree assigned by G0. Read applicable repository instructions, `00_EXECUTION_HANDBOOK.md`, the canonical revision-5 decision context and ownership/contract manifest. If G0 has not run, execute `01_BOOTSTRAP_CONTRACTS_AND_WORKTREES.md` first. Continue through this task; do not stop after each subgate for routine permission.

Goal: a real callable personal matching service over the supported catalogue, preserving industry assessment and feedback rules, plus actual Ridge/gradient-boosting experiments where valid targets exist. Reuse working G1A/G1A-R code while removing the incorrectly mandatory preparation-plan dependency from INITIAL matching through an explicit versioned change.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| A1.1 | Source-grounded catalogue ingestion and actual runtime loading | Catalogue/service coverage checkpoint |
| A1.2 | Industry assessment and initial personal role-fit service | Real profile-to-role result and trace checkpoint; no mandatory learning-plan dependency |
| A1.3 | Preference feedback, reset and explicit search filters | Verified feedback semantics and service checkpoint |
| A2.1 | Baseline/Ridge/boosting training pipeline and target/split manifests | Runnable learner pipeline checkpoint; label limitations explicit |
| A2.2 | Execute/evaluate candidates and record model selection | Experiment/evaluation checkpoint, or honest blocked/limited status |
| A3.1 | Publish the final personal-service handoff | Culminating A checkpoint with phase/refinement SHAs and current readiness |

## Ownership

Own catalogue ingestion/normalisation and role mappings, profile-to-feature calculations, personal fit and recommendation policy, personal-model training/evaluation, per-lane artifacts and tests. Own shared contracts/root dependency files as integration owner; apply C/B requests in coordinated small commits. Do not edit their module internals, C migrations/API routes, or B market data outputs concurrently. Only B launches paid RunPod jobs.

## A1 — deliver an actual broad-catalogue baseline service

1. Enumerate acquired role sources, versions, IDs and field coverage. Distinguish raw, normalised, runtime and per-profile scoreable coverage. Locate the cause of any three-role allowlist or limited fixture loader. Count actual records; do not hardcode previous 0/18 results.
2. Ingest all eligible acquired records through source-grounded batch rules. Preserve taxonomy/version identity, provenance and meaningful skills/tasks/interests/work-context fields; do not fabricate crosswalks or turn vague descriptions into verified measurements. Only collect additional specific missing source fields when necessary, within available access.
3. Keep initial occupational matching independent of a complete personalised roadmap, estimated exercise hours or custom learning milestone. Retain preparation feasibility for the later pathway service. Version changed score meaning and adapt consumers; do not simply remove old components and silently renormalise weights.
4. Implement the declared industry assessment from current background and preferences. It influences ranking; it does not hard-filter industries. Support no employment history, multiple fields and a desire to leave the current field. Preserve transferable evidence.
5. Implement typed role/industry preferences, including Interested, Not interested, reset and explicit view filters. Unknown is not dislike. Repeated feedback is idempotent. Negative preference changes the declared preference contribution, not skills or external demand. Avoid double counting and inappropriate propagation across a role's many industries.
6. Implement personal fit, supporting reasons, gaps, prerequisites and unknowns under the numerical contract. Distinguish potential direction from qualified-to-apply-today. F is an index unless a probability target/calibration actually exists.
7. Expose the committed service boundary for C. Consume B's current/forecast interface without inventing data or collapsing periods. Keep score provenance and availability; do not substitute 0 for missing D. Apply only a compatible approved combination rule, and expose unresolved mode choices explicitly rather than guessing them in the chat layer.
8. Give C actionable role requirements/gaps for pathway generation; do not make C author every occupation manually. Publish a useful service commit early for I1, before all learner optimisation is complete.

Demonstrate actual service calls with existing profiles plus explicitly synthetic complete profiles covering the D02 audience types. Preserve existing unknown evidence. Report before/after counts on unchanged original profiles and separately the synthetic demonstration results. Do not claim the synthetic cases establish real-world accuracy.

## A2 — implement and run the personal-fit learners

Inspect existing baseline/Ridge/XGBoost paths and artifacts first. Implement or repair reusable preprocessing, training, persistence, inference adapters and policy/schema compatibility checks for all agreed methods. Do not create dummy learner stubs to satisfy the gate.

Identify the target labels and their provenance. Use independent suitable labels if available; split by profile/group so near-duplicates do not leak. If only policy/LLM-generated provisional labels exist, keep them visibly provisional, freeze the generation method and evaluate agreement with that teacher separately from empirical personal-fit validity. Never relabel them as independent. If no legitimate target can be supplied, report that supervised fitting is blocked and complete the baseline, pipeline, fixtures and handoff; do not falsely claim all A2 criteria passed.

Prepare executable, bounded training jobs with actual data/schema/policy IDs, hyperparameters, splits, expected resource use and outputs. Request B to run the required RunPod jobs from an immutable commit/manifest; do not independently spend or race the account. CPU smoke tests may run locally. A owns the model logic and artifact acceptance even when B operates the remote job.

Compare the methods on the same held-out cases. Explain chosen metrics and limitations. Record training succeeded/failed, evaluated, selected and active separately. A retained baseline is allowed if supported by evidence, but does not excuse omitting Ridge/boosting work. Do not assume a failure means a need for more complexity; investigate data, targets and implementation first.

## A3 — evidence and integration responsibility

Meaningful checks: cross-industry options survive; unknown preferences remain unknown; a negative-interest state lowers its declared contribution and never rewrites market evidence; resets work; no milestones required for initial matching; malformed/missing records have precise status; trained artifacts cannot load against incompatible schemas; service results reproduce their trace.

Return machine-readable catalogue/scoring coverage, experiment manifests/results, service examples and a concise lane report. Include exact commands, commit SHAs, artifact paths, real remaining blockers and unrun checks. Avoid another giant tooling-only report with no runtime output.

Merge early B/C contract-compatible slices as integration owner only after clean handoffs; do not interfere with their ongoing files. When ready, execute `05_INTEGRATION_AND_LIVE_ACCEPTANCE.md`. Keep root/lockfile decisions moving so other sessions do not wait unnecessarily.

Acceptance: broad actual catalogue loaded; real profile-to-role service results with defensible missingness; approved feedback semantics; model code and genuine experiment status; C can consume results. Coverage, empirical quality and deployment are separate claims.
