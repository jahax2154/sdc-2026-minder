# G3 — coverage and bounded learner experiment

**Implementation/tests PASS. Real CPU fit/reload verification BLOCKED by missing funded RunPod access. Independent quality NOT_EVALUATED. Baseline retained.**

The available implementation and local checks are complete; the requested real learner fitting experiment has **not** completed. No model was trained locally as a substitute. [Execution authorization](G3_authorization.json) binds the [actual instruction](G3_instruction.txt) by SHA-256. Earlier gate reports and the canonical policy at `ml/docs/MINDER_POLICY_REVIEW_v1.md` were reused; its machine JSON projection and historical approval fields are unchanged. No duplicate policy pack was introduced. [Evidence](G3_evidence.json), [checks](G3_checks.txt), [coverage](G3_coverage.json), [market indexes](G3_market_indexes.json), [execution statuses](G3_execution.json) and [service checks](G3_service_checks.json) and [actual profile readiness](G3_profile_readiness.json) contain actual results.

## Measured coverage

All **11 acquired source-file hashes match their manifest**. The Phase 2 DOSM workbook/derived-table parser validates **952 source observations/cells**, with **921 numeric**, **31 missing**, and **0 rejected**. Numeric observations are market measurements, not user-role examples.

| Family | Rows | Numeric | Missing | Actual grain/scope |
| --- | ---: | ---: | ---: | --- |
| Published occupation activity | 308 | 282 | 26 | Malaysia, quarter, published broad occupation label |
| Published industry activity | 644 | 639 | 5 | Malaysia, quarter, published economic-activity label |
| Independently reviewed personal-fit labels | 0 | 0 | — | No eligible user-role labels/groups |

The offering observations span **2019-Q3–2026-Q2**, within one pinned 2026 release vintage. Taxonomy/method revisions not supplied by the publisher remain unknown; comparisons stay within the same release and published labels. Annual wage/state labour sources, occupational skill references, the ESCO crosswalk and AI-task evidence remain distinct source families; they were not merged into training targets or unsupported joint observations.

`G3_coverage.json` enumerates all six actual proposed criterion IDs, role versions, absent accepted milestone IDs, matching assessment counts, six synthetic profiles/family IDs, goals, education/experience, weekly time, budgets/access/preferences, source evidence states, geography, industry labels, periods, measurement grain and evidence types. **Six declared synthetic family IDs are not six independently labeled groups; the latter count is zero.** All six criteria lack anchored known profile assessments and accepted real-role milestones. Existing profiles and labels were preserved.

The five highest-impact missing factors, with affected decisions, are:

1. Accepted bounded milestones/effort and explicit profile measurements: whether any of the existing 18 pairs can receive personal-fit F.
2. Compatible independent labels across profile families: whether learner agreement can be evaluated or a learned candidate recommended.
3. Fine-grained Malaysian role observations and defensible mappings: whether the three actual O*NET roles can receive D/combined S.
4. Observed skill-tagged and employer-resolved activity: whether skill/employer counts or indexes are available.
5. 2026-Q2 industry classification continuity and observed joint/regional/international slices: whether current industry growth/indexes or cross-slice comparisons are defensible.

No new scraping, source acquisition or arbitrary industry expansion occurred.

## Supported observed market indexes

`market_indexes.py` reuses Phase 2 canonical observations, published-total share and exact-prior-year-quarter comparability checks. It implements the declared fixed-universe midrank formula:

`D_activity = 100 × (0.60 × P_U(share) + 0.40 × P_U(YoY))`, minimum eligible N=5.

The named specification is **dosm-observed-offering-activity-v1**: provider-defined observed offering activity at the source's published grain, not hires, independently deduplicated advertisements, narrow-role demand or a future forecast. Cohorts stay separated by source/release, population/method, geography, taxonomy, dimensional grain, unit and period. Only categories with valid share denominators, comparable positive prior counts and valid quality enter U. Unknown values, zero prior bases, unclassified records, flagged continuity and missing history are disclosed exclusions. No missing indicator is imputed or reweighted.

Actual outputs: **56 source-period cohorts, 47 eligible, 9 without indexes; 667 index values**:

- **24 occupation cohorts / 192 values**, through 2026-Q2. Latest eligible cohort N=8.
- **23 industry cohorts / 475 values**, through 2026-Q1. The flagged 2026-Q2 industry cohort has N=0 and no index.
- The first four quarters lack exact prior-year history. The source's industry continuity flag explains the additional unavailable cohort.

Each cohort retains original/eligible population IDs, exclusions, raw count/share/YoY, source cell, size, formula and a snapshot-bound cohort hash. `project_index_rows` looks up saved values and never rescales against a user's candidate list. Ties receive midrank percentiles; all-equal cohorts return 50. Cohort minimum is a declared product guard, not a statistical adequacy claim.

For example, the published **Managers** group in 2026-Q2 has 87,950 offerings, share 0.158323 of the published 555,509 total, YoY +79.989%, and activity index **66.25** within the eight eligible broad groups. Source sheet/cell and prior/denominator observation IDs are retained. This is not a demand measurement for Software Developers, Data Scientists or Information Security Analysts.

No defensible narrow-role allocation/mapping exists, so **D and S stay null for the entire actual recommendation comparison** and `personal_fit_only` remains unchanged. Broad activity indexes are evidence/trend outputs only. Skill/employer views, separate-marginal joint views and forecasts remain unavailable. No schema migration or replacement of the G2 recommendation interface was needed.

## Learner execution and provenance

The existing learner configurations are preserved: StandardScaler+Ridge (alpha=1, SVD) and CPU histogram XGBoost (100 trees, depth 2, learning rate .05, min child weight 5, lambda 10, seed 42, n_jobs=2). Thread limits remain 2. Both packages import and the expected pipelines construct in the existing local environment; this is **preflight**, not fitted-model verification.

Existing `training.smoke` now completes one bounded run through the **same `inference.recommend` service** when an authorized runner is supplied: fit, save full pipeline, reload, verify finite/aligned predictions within **1e-9**, then exercise baseline/Ridge/XGBoost service outputs on the same 32 mathematical fixture rows. It persists fixture inputs, predictions, service results, settings, dependency/code/policy hashes, actual runner/environment/timing and agreement diagnostics. The fixture has continuous mathematical targets; it is not an independently reviewed 0/1/2 relevance dataset. There is no independent holdout or quality claim for this control.

Artifact metadata is versioned as **minder-learner-artifact-g3-v1** and distinguishes provenance from evaluation status. Unclassified, synthetic and distillation artifacts cannot enter the independent-serving loader. Explicit research calls may use the added optional `artifact_mode="synthetic_math_only"` or `"policy_distillation"`; the default remains `independent_reviewed`. Research results carry an EXPERIMENT ONLY warning and stay non-promotable. Exact compatibility, policy hash, package versions, implementation hashes, pipeline integrity/shape and fitted-state checks are retained. Unclassified legacy artifacts require provenance/compatibility review; they are not silently grandfathered into serving. There were no actual trained artifacts to migrate.

`compare` retains grouped development validation and a frozen family holdout when feasible, with preprocessing fitted within training groups only. It now also persists aligned development out-of-fold predictions; MAE is reported both as served F/50 versus grade and as the corresponding 0–100 index error. Existing linear-gain NDCG@3, same eligible candidate sets, IDCG=0/all-weak cases, clipping, ties, gaps and counterfactual checks remain. `final_evaluate` rejects experimental provenance. Baseline-first tie preference and explicit candidate selection remain; no active-model switch was added.

| Execution/evidence gate | Actual result |
| --- | --- |
| Local CPU dependency/pipeline construction | PASS, both pipelines constructed; no actual learner fitted |
| Experiment control flow and serialization/service path | PASS using clearly labeled test stubs in temporary directories; not real learner parity |
| Real Ridge/XGBoost fit/predict/save/reload parity | **BLOCKED / unmeasured** |
| RunPod execution/credit/budget | **Not verified; no run** |
| Optional policy distillation | **Not run**; no compatible G1B proposal targets found |
| Independent baseline/learner quality | **not_evaluated**, zero eligible rows/groups |
| Model recommendation / active scorer | **Keep baseline**, no evidence supports learner selection |

No RunPod environment names, local env files, CLI/configuration, SSH target or connector were found in the inspected setup. There is no verified CPU target, credit applicability, account balance or agreed current budget. Unknown balance is not zero. A direct smoke attempt with no runner evidence was rejected **before fitting, constructor invocation or run-artifact creation**. No account query/provisioning or spending was attempted without access. RunPod fit/prediction/reload durations and parity are null/unmeasured, not successful or zero.

The optional distillation fitting experiment was not created from G1A-R draft templates or disguised as independent data. Controlled tests exercise mode separation only. The independent annotation CSV remains empty, so actual baseline and comparison commands both return `not_evaluated`; no fictitious profile split or holdout was manufactured. The supervised implementation is ready, but empirical comparison metrics are unavailable:

| Candidate | Eligible independent rows/groups | NDCG@3 | Served-score MAE | Real fit/reload |
| --- | --- | --- | --- | --- |
| Baseline | 0 / 0 | not_evaluated | not_evaluated | fixed policy; no fit needed |
| Ridge | 0 / 0 | not_evaluated | not_evaluated | blocked |
| XGBoost | 0 / 0 | not_evaluated | not_evaluated | blocked |

## Verification, integration and limits

**100 tests passed**, unittest time **110.355 s**, process wall time **110.470 s**, local existing `ml/.venv`. New tests cover exact midrank values, tie handling, minimum N, zero current/positive prior versus zero base, quality exclusions, provider separation, duplicate revisions, frozen projections, runner-before-fit guards, non-promotion, policy compatibility and controlled smoke/service round trips. Existing grouped split/holdout-use, all-weak/clipping/tie, feature/constraint and artifact tests also pass. Test stub estimates/timings/runner flags are not actual RunPod or independent review evidence.

The six actual synthetic profiles were also rerun through `recommend_profile`; all six envelopes validate and all 18 pairs remain explicitly unscored with missing milestone definitions. No supplied answers were filled. Current service checks validate against the unchanged strict result contract: foundation vector **67**, explicit missing Ridge/XGBoost -> **model_not_ready**, common D/S null. Both the existing 35-test foundation suite and full 100-test suite passed. All acquired data, pending labels, old reports, G1A/G1A-R code and app/contract/configuration files outside the four explicitly extended ML modules were preserved. No dependencies installed, real models fitted, labels generated, commits/pushes/publishing or spending occurred.

Task-file syntax/whitespace, credential-pattern and binary checks pass. Repository-wide `git diff --check` still flags the preexisting trailing space on `checked_rows`; adding the math import moved its location from training.py:17 to **training.py:18**. The unrelated whitespace was preserved. Scoped scanning is not a complete secret-detection guarantee.

G2's optional-keyword default and typed output remain backward compatible. No chat/frontend files were edited. At inspection only the G2 task document and app scaffolding were present; no G2 completion report or live endpoint was available to exercise. ML callable/contract checks passed; no live chat/HTTP/frontend pass is claimed.

## Next usable interfaces and remaining dependencies

- Inventory: `PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.g3`.
- Frozen market evidence: `market_indexes.build_indexes(observations)` and `project_index_rows(report, observation_ids)`; current outputs are `G3_market_indexes.json`. Do not map broad values onto narrow roles.
- Actual funded CPU machinery run, **only on the verified RunPod pod**: `PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence smoke --run-id g3-synthetic-machinery --runner-evidence /path/to/actual-private-runner-evidence.json`.
- Independent comparison: existing `baseline-evaluate`, `compare --data ... --runner-evidence ...`, then controlled `final` after a frozen development selection. These require genuinely compatible independent labels; this gate does not generate them.

Remaining dependencies are the existing valid milestone/profile inputs, independent labels, funded/attested RunPod target, compatible fine-grained market mappings and unresolved industry continuity. Their effects are separate in the evidence. **No model improvement, outcome accuracy or completed learner experiment is claimed. Stopped after G3's available completion report.**
