# Session B — bounded synthetic experiment, not manufactured market evidence

Read 05_SYNTHETIC_DATA_POLICY.md. Existing real source delivery remains intact.
Do not restart the completed acquisition search without a specific new source lead.
Do not change the approved real forecast target to make simulated results appear eligible.

## SY1 — audit existing simulations and create only missing cases
You already reported synthetic pipeline exercises. Reuse the generator, feature code, estimators
and test harness where they exist. First identify the additional question each new case answers.
If all cases already exist, record that evidence rather than producing another redundant dataset.

Create the smallest reproducible dataset needed for:
- stable, rising and falling demand;
- seasonal variation;
- abrupt changes;
- sparse series, actual zero counts and missing collection periods;
- changed source coverage/denominator;
- correlated roles/skills with declared relationships.

These are scenario families, not discoveries about actual Malaysian roles.
Use fictional aggregate series by default. Do not ingest CVs, real user profiles or restricted source
records to manufacture volume. Real anchors may be used only with permitted reuse and an explicit
link to the aggregate statistic they constrain, without pretending that detailed paths are observed.

Store a generation manifest: purpose, assumptions, generator/version, random seed, parameters,
units, simulated timeline, any real aggregate anchors, permitted uses, limitations and hashes.
Mark records/data/artifacts synthetic and segregate namespaces, artifact paths and dataset IDs.
Keep source-collected observations read-only and unaltered.
Commit SY1 with examples and the isolation checks.

## SY2 — run bounded training/evaluation
Split complete source/series/scenario groups before fitting preprocessing or a data generator.
For forecast experiments preserve chronological ordering within a series; do not let future values
enter lag construction or fitting. Keep related variants out of both train and test.
Use a separate validation set for tuning; do not select winners repeatedly on the final test set.

Run existing last-value baseline and applicable seasonal baseline, Ridge and XGBoost on the SAME
eligible synthetic task/split. Do not compare different targets as one leaderboard.
Start with a small run to measure time/memory; avoid a large hyperparameter search.
Report MAE and other existing appropriate metrics per scenario, their units and missing/zero handling.
Report robustness to a different scenario family as simulation robustness, not real-world accuracy.

If real target-compatible holdout data exists, preserve it untouched and report an additional
real-data evaluation separately. If absent, record independent real validation as unavailable.
Tests against the generator's outcomes measure simulated performance; policy-generated labels
measure policy imitation. Neither validates real Malaysian demand.

Export model artifacts with dataset/label lineage and synthetic-only serving eligibility.
Do not replace the active real recommendation policy or activate the public forecast.
Commit SY2 with actual logs, metrics and baseline comparisons, not merely planned commands.

## SY3 — reproducibility, RunPod readiness and handoff
Demonstrate that normal runtime cannot load synthetic market evidence/model artifacts as observed
national evidence. A scenario dataset cannot increase real-source coverage counts.
Give A any minimal integration contract request; don't edit its scoring implementation.

Prepare a RunPod-ready bounded job specification using the same code/data hashes:
entry command, dependencies, CPU/GPU setting, timeout, worker/concurrency limit, estimated costs,
artifact outputs, cleanup/scale-down and evidence to capture.
Verify access/balance only if authorized credentials are available. Existing paid-run authority
governs execution; the Git push authorization in this pack does not itself authorize paid jobs.
If execution is not authorized/available, report a concrete runnable job and exact blocker.
Do not claim RunPod use until an actual job has run and evidence is saved.

Write a dataset/model card and submission-ready factual paragraph:
observed data sources vs synthetic data, generation assumptions, train/validation/test method,
what the metrics measure, selected normal-runtime model and unavailable capabilities.
Do not say the pipeline is independently accurate because it fits simulated labels.

Commit SY3 and report full SHA to A for the authorized coordinated push.
Stop once these outputs are complete; more generated rows alone are not progress.
