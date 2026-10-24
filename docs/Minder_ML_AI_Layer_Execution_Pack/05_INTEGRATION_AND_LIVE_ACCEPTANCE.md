# Session A — integrate, verify actual user flows and finish the AI/ML layer

Run in the verified A integration worktree. Read the canonical decision context, handbook, ownership manifest, numerical contract and each lane's current handoff. This task starts with incremental I1 integration and concludes with I2; it is not an instruction to wait for every experiment before connecting services.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| I1.1 | Merge and verify the first real profile-to-service-to-chat slice | Early integrated checkpoint before all training is finished |
| I2.1 | Merge remaining modules, migrations and artifacts | Integrated compatibility checkpoint |
| I2.2 | Exercise required user flows and repair phase-linked defects | Acceptance checkpoint; fixes retain original phase IDs |
| I2.3 | Prepare release and verify authorised deployment if accessible | Release/deployment evidence checkpoint; no Git push without instruction |
| I2.4 | Consolidate status/evaluation and freeze handoff | Culminating integration checkpoint; remote push remains pending |

## I1 — first working integration slice

Obtain clean commits from A1, B1 and C1 with a common contract version. Inspect their diffs/reports and merge compatible slices preserving meaningful history. Coordinate before touching a still-active owner's files. Do not force overwrite conflicts or use a squash merely to hide the development sequence.

Resolve actual dependency/import/schema/config differences and migrate one isolated integration database in the declared order. Ensure source/model artifacts are accessible in this environment using documented IDs/paths/checksums, not another developer's home directory. Align feature generation between training and runtime.

Demonstrate early: persisted profile -> actual role candidate selection/personal assessment -> real available market evidence or explicit unavailable result -> public API -> grounded Groq response (if accessible). A fixture-only screenshot is not this check. Report the precise layer blocking any failed hop and send the actionable fix to its owner while independent work continues.

## I2 — merge remaining outputs and inspect behaviour

Bring in A2, B2 and C2/C3 (plus optional D only if actually assigned). Verify exact selected artifacts, versions, model task, source scope and fallback states. Do not confuse successful training with live activation. Remove accidental production use of mock profiles, fixture providers or fake source data while keeping named test fixtures for tests.

Exercise the following end-to-end scenarios through the actual application/service boundaries:

1. Fresh graduate/student with no prior industry: supported intake and matching still work; actual unsupported fields are explicit.
2. Career switcher: roles outside current industry remain considered; industry affinity is present in the trace; no hidden x-threshold filtering.
3. Not interested feedback: label persists, declared preference contribution falls, repeated clicks do not accumulate penalties, market evidence unchanged, reset works.
4. A complete explicitly synthetic demonstration profile produces real service scores against real role references; original profile coverage is reported separately. This is demo evidence, not independent accuracy.
5. Current conditions: user receives explanations/resources, not internal market-score matrices. Source dates are visible where relevant.
6. Next-quarter outlook: supported observations/projections and target quarter are distinct; no forecast yields an honest unavailable state, not fabricated charts or silent current-value substitution.
7. Company Explorer: official Malaysia-based MNC evidence; recommended role checked; missing role described as not found in checked sources; alternative company roles assessed separately; main recommendations unchanged.
8. Chat/CV update: explicit information reaches the scoring profile; uncertain inferred changes are proposed rather than silently applied.
9. Direct command to move a task: valid request executes once without redundant approval and success reflects a persisted write.
10. Daily/market-triggered suggestion: a proposal is created with no mutation; Approve applies the exact diff, Reject preserves state; stale/conflicting proposals are handled safely.
11. Task completion and time/preference change: proper state/event propagation, preservation of completed work and no automatic certification of competence.
12. Provider failure, missing forecast, incompatible model artifact and failed write: clear bounded failure/fallback; no invented explanation of success.

Use meaningful checks targeted at these risks. Reuse existing tests where valid; do not inflate test counts with tests mirroring implementation. Separate local, simulated-event, real-provider and deployed checks. Stop optional testing once concrete remaining risks are resolved.

## Evaluation and evidence consolidation

Publish one concise integration report referencing per-lane artifacts rather than duplicating reports. Required fields:

- code revision, policy/schema/model versions and selected live methods;
- raw/normalised/runtime role counts; score coverage on original versus synthetic profiles;
- current evidence and forecast coverage separately for roles and skills;
- baseline/Ridge/gradient-boosting implementation/run/evaluation/selection status;
- forecast holdout dates, target quarter, metrics and simple-model comparisons;
- personal-fit label provenance and what validity is or is not established;
- actual provider/model, trigger/approval checks, data isolation and scheduler status;
- actual RunPod/Replit/Groq usage when available and any exceeded/unavailable resource;
- examples with source links and experimental evidence; no secrets or unsupported accuracy claims;
- remaining source/access limitations and unrun checks.

Every component has separate implementation, data, empirical evaluation and live integration states. A trained candidate failing promotion does not force its deployment. Missing historical data may legitimately produce unavailable forecasts, but report forecasting experiment limitations plainly. Do not issue an unconditional 'AI/ML complete' if required learner runs, live provider calls or core user flows remain blocked.

## Deploy and verify

Use the existing authorised Replit/project deployment path and current team release ownership. Do not create new paid infrastructure, spend beyond the supplied budget, replace production data or change DNS without the applicable authorisation. Verify configured secrets by presence/use without printing them.

Confirm the server process, database migrations, artifact loading, outbound source access, Groq access and scheduled-worker behaviour on the deployed build. A local test cannot prove a sleeping host runs daily jobs. If deployment access is missing, finish a concrete reproducible build/release checklist and state the exact missing access; do not claim the site is live.

Coordinate minimal frontend wiring with its owner for the exact navigation. Do not leave real API integration until a presentation demo. Record the live URL and deployed commit only after verification. Produce a truthful final checkpoint and freeze the submission revision; retain actual development commits. Keep this checkpoint local. Push only after an explicit user instruction and verification of the intended remote/branches; no force-push or fabricated history.

Final response: what works live, link/revision, which model actually serves each target, actual evaluation/coverage, unfulfilled items, and exact operational handover. Do not substitute a plan for the authorised integration work.
