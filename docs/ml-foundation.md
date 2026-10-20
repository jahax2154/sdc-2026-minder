# Minder ML foundation

Implementation authorized by [the supplied execution task](../ml/docs/MINDER_ML_FOUNDATION_CODEX_TASK.txt), 20 October 2026. This authorization supersedes Task 001's scaffolding-only limits for this bounded module. Broader runtime and application decisions remain open.

The baseline is the configured default. Ridge and XGBoost are executable offline paths, not validated career models. See [actual local check evidence](../ml/evaluation/foundation_checks.json) for command exit codes, outputs, dependency versions and gate status. No model fitting was performed locally or on RunPod in this task. No paid resource was created.

## Actual layout and application boundary

Existing `ml/src/minder_ml` is extended with `intelligence/`: schemas, features, scoring, estimators, evaluation, training, artifacts, inference, an explicitly disabled LLM adapter and a CLI. The pre-existing empty `algorithm.py`, `ridge-regression.py` and `gradient-boosting.py` files are preserved. No second package or backend is introduced.

`recommend(roles, profile_version=..., evidence_snapshot_id=..., role_catalogue_version=..., preparation_horizon_weeks=12, scorer_kind='baseline', model_version=None)` is the single callable application entry. `RoleInput` contains an immutable validated `FeatureSnapshot` and evidence IDs. The CLI `score` uses that same service. `apps/backend-api` has module placeholders but no runnable API/routes to extend; no HTTP integration is claimed. A future route should adapt validated inputs to this callable rather than duplicate scoring.

Exact result structure is owned by [recommendation-result.v1.schema.json](../contracts/recommendation-result.v1.schema.json). It includes feature/model/score/ranking versions, profile/catalogue/evidence versions, horizon, known components, Q, raw diagnostic predictions, scored options and explicit unscored reasons. No artificial top score or arbitrary cutoff is introduced. All eligible roles are returned in descending served F, breaking ties by ascending role ID; fewer than three remain fewer than three.

An explicitly requested learner without a compatible, development-selected, holdout-evaluated artifact returns `model_not_ready`, with no baseline fallback. Smoke/development-only artifacts are rejected. Artifact availability does not change the baseline default. A horizon mismatch requires rebuilt features; learned requests additionally must match the artifact's documented target horizon and catalogue.

The LLM interface accepts a completed result and selected evidence. The disabled implementation returns no evidence claims or proposed changes and leaves numerical results unchanged. Typed future proposals require backend validation/user acceptance. An LLM has no artifact-writing, canonical URL or score authority. Updating weekly availability rebuilds features, not models.

## Features and target

The allowlisted order is `[skill_coverage, interest_alignment, time_feasibility, resource_feasibility, work_style_alignment]`, version `personal-preparation-features-v1`. Each value is finite in [0,1] or unknown. IDs, provenance, labels, Q and market data never enter X.

Skill coverage uses reviewed, nonnegative initial-milestone requirement weights: C_observed is weighted demonstrated criterion fraction among assessed requirements; Q is assessed weight divided by total weight. Unknown is not zero. No assessed positive weight gives C=null/Q=0. An absent, empty or invalid catalogue raises a catalogue validation error rather than implying user inability. Only complete vectors with Q=1 within 1e-9 are scored. No imputation, partial-evidence ranking or silent reweighting occurs. Ordinal O*NET skill levels are not treated as ratio-scale proficiency.

The explicit reviewed-input rubric for this foundation is:

| Component | Reviewed interpretation |
| --- | --- |
| I | Assess alignment of explicitly stated interests with reviewed role activities: 0 = documented conflict/no alignment, 0.5 = documented partial alignment, 1 = documented direct alignment. Unknown interests remain null. |
| R | Review required initial resources against available resources: 0 = unavailable, 0.5 = documented partial feasibility, 1 = feasible. Use a documented weighted checklist if multiple resources matter; unknown required resources remain null. Known no additional required resources gives 1. |
| W | Review explicitly stated work preferences against role conditions using the same 0/conflict, 0.5/partial, 1/aligned rubric. Multiple preferences use a documented weighted checklist; unknown preferences remain null. |

Reviewed fractional aggregates within [0,1] may be supplied with their checklist/evidence IDs. The role catalogue must document the criteria, weights and aggregation used. A neutral-looking 0.5 must never stand in for unknown. No text/personality inference is implemented. These are prototype review rubrics, not established empirical measurement scales.

T=min(1,h*H/E) for reviewed E>0; known E=0 gives 1, and missing required inputs give null. h=0 and E>0 gives 0. Negative/nonfinite inputs are invalid. H defaults to 12 positive weeks and is stored in the snapshot. `build_features` retains h, the E used and optional reviewed low/high effort bounds separately; bounds never enter the model. A supplied time snapshot with derivation evidence must agree with the recorded calculation. Reviewed cached snapshots may be used without recalculating their meaning; the CSV horizon and evidence/provenance must identify their conditions.

Target `personal-preparation-grades-v1`: 0 weak, 1 plausible, 2 strong preparation relevance for a user-role pair under the stated horizon, excluding market attractiveness. Treating ordinal grades as equally spaced is a prototype assumption. None of these quantities measures hiring probability, readiness certification or employment outcomes.

## Scorers and market boundary

Baseline F0=100*(0.40*C+0.20*I+0.20*T+0.10*R+0.10*W). These are manual starting preferences. Weights must be finite, nonnegative and sum to 1 within 1e-9; malformed weights are rejected. The golden vector [0.6,0.8,0.5,1,0.7] scores 67. All-low inputs remain low on the fixed scale.

Ridge is `StandardScaler` followed by `Ridge(alpha=1.0, solver='svd')`. The scaler is fitted inside each training fold only; constant columns use library behavior. The factory also permits 0.1 and 10, but this CLI performs only the fixed 1.0 comparison. Ridge's L2 value is unrelated to fit_weight. XGBoost uses `reg:squarederror`, CPU `hist`, device=cpu, n_jobs=2, 100 depth-2 trees, learning_rate=0.05, min_child_weight=5, reg_lambda=10, full row/column sampling and seed 42. No ensemble or early stopping is used.

Both learners retain raw grade predictions and serve F=100*clip(y_hat/2,0,1), version `grade-to-index-v1`. Training and inference share feature validation/selection, prediction execution and score mapping. No candidate-list normalization or softmax is used.

The separate pure `combine(F,D,fit_weight=0.7)` validates scales and returns S=fit_weight*F+(1-fit_weight)*D; 67 and 80 give 70.9. No comparable real market assessment is supplied, so this service deliberately uses `personal_fit_only` for the entire set, and returns D/S=null. fit_weight is recorded but unused in this mode. Raw market evidence remains separately owned by its source manifest/caller and can be referenced through evidence IDs. No market index is manufactured from DOSM/ILO statistics. Enabling combined ranking later requires comparable geography, occupational mapping, observation period, horizon, scenario and index/policy versions across the set and a separately versioned contract/policy.

## Data and evaluation safeguards

The original source pack is preserved at `ml/minder_ml_starter`, including provenance and attribution. Its official reference rows are not personal-fit labels. No production catalogue is fabricated. The new [annotation template](../ml/data/annotations/personal_fit_annotations.csv) has a header only; its [JSON equivalent schema](../contracts/personal-fit-annotation.v1.schema.json) specifies typed records. CSV booleans are `true`/`false`, grades are `0`/`1`/`2` and unknown values are blank. The starter template is preserved; it lacks the new feature/rubric versions and independent-review attestation columns.

Empirical rows require reviewed status, complete eligible features, reviewer ID/reason, explicit independent-review attestation, profile/group/role IDs, profile/catalogue/feature/rubric versions, a positive horizon and a grade. The prototype accepts explicitly synthetic profiles only, following the PRD's no-personal-data constraint. An attestation is a review-process claim to be supplied by actual reviewers, not something a validator can independently prove. Pending grades stay blank. Validation fixtures exercise acceptance/rejection using explicitly fictional review fields; they are never empirical evidence. No reviewed label has been created by this implementation.

One run uses one horizon, catalogue, feature schema and target rubric. Duplicate profile-role rows and inconsistent profile/group mappings are rejected. The proposed 25-group × 8-role pilot is a planning target, not proof of adequate data. A supplied manifest assigns every group exactly once to development or holdout. Otherwise seed 42 freezes about 20% of groups before comparison (25 groups gives 20 development/5 holdout). Fewer than five total groups use exploratory development only; fewer than two development groups are not evaluated. Small holdouts remain limited pilot evidence, never an adequacy claim.

Development uses GroupKFold, at most five folds, and identical eligible candidate sets for all scorers. Selection uses out-of-fold linear-gain NDCG@3, then served-grade MAE, then baseline-first deterministic ties. No final holdout is used for tuning. Only the frozen selection and predeclared baseline are evaluated on holdout. Split/data/snapshot/pipeline/selection/development-metric hashes are checked. Persistent exclusive markers prevent accidental repeated evaluation in a run or another run using the same dataset/split. A failed attempt also consumes its marker; investigate rather than deleting markers and presenting reuse as independent. These local safeguards do not replace team discipline or protect against deliberate artifact edits.

NDCG@3 uses sum(y/log2(position+1)) with linear gains and deterministic served order, divided by the ideal DCG over the same candidates. Profiles with IDCG=0 are listed separately and excluded from the NDCG mean. Reports include candidate counts/annotation coverage, served-grade MAE, clipping rate, tied score pairs, all-weak profiles and bounded counterfactual reversals (at most 20 rows, +0.1 per feature within bounds). Baseline monotonicity follows from nonnegative weights; learners have no such guarantee. Reversals require review and may justify continued baseline use. No monotonicity constraints are tuned here. Missing-input behavior is verified by contract/math tests, not claimed as a dataset quality metric.

## Execution and artifacts

All real estimator fitting, including synthetic smoke fitting, requires an operator-verified, credit-funded RunPod CPU runner for this task. No RunPod connection, Pod ID, credit applicability or current budget was available to verify in this session. Existing submission PDFs do not establish a currently executable runner or remaining credits. No account access or paid resource creation was attempted.

On the actual runner, an operator must supply a private JSON verification file with `execution_location: "runpod"`, `cpu_only: true`, actual `pod_id`, `verified_by`, `verified_at`, `credit_applicable: true`, `credit_applicability_reference`, `agreed_budget_usd`, and `estimated_run_cost_usd`. Values must be real; estimated cost must fit the agreed budget. `RUNPOD_POD_ID` must match the verified pod. This is an explicit operator attestation, not an account-balance API check. Do not fabricate it or store secrets in it.

Artifacts go under ignored `ml/artifacts/intelligence/<run_id>/`: complete pipeline per learner, metadata, metrics, frozen split/selection/validated snapshots and heldout predictions when evaluated. IDs are restricted and paths checked; no arbitrary request path is accepted. Joblib can execute code: load only team-created files in this controlled location. Hashes detect accidental changes, not maliciously rewritten manifests. Serving checks exact dependency/Python versions, implementation hashes, feature order/versions, catalogue/horizon and evaluation status.

Metadata records actual platform/CPU information, bounded thread settings, resolved versions, hyperparameters, dataset/split hashes, wall/process fit time and repeated inference timings (10 repetitions, batch up to eight, including thread-limit context). Threadpool limits and XGBoost n_jobs are two. No CPU utilisation percentage, peak memory or latency percentiles are claimed. Smoke artifacts are labelled `synthetic_smoke_only`, separate from empirical reports and never selectable for recommendations.

## Runnable commands

From repository root, create an isolated environment and install the declared CPU dependencies if needed. Linux XGBoost requires a working OpenMP runtime (typically libgomp); the local Mac import failed because libomp.dylib is absent. This task did not modify system libraries.

```sh
python3 -m venv ml/.venv
ml/.venv/bin/python -m pip install -r ml/requirements-foundation.txt
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence checks
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence preflight
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence validate --data ml/data/annotations/personal_fit_annotations.csv
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence score
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence score --scorer ridge
```

The exact remaining CPU machinery command, **on the verified RunPod runner** after dependency/OpenMP preflight passes, is:

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence smoke --run-id foundation-smoke-001 --runner-evidence /path/to/verified-runpod-cpu.json
```

After genuine independent annotations and a reviewed catalogue are supplied:

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence compare --data ml/data/annotations/personal_fit_annotations.csv --run-id reviewed-pilot-001 --runner-evidence /path/to/verified-runpod-cpu.json
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence final --data ml/data/annotations/personal_fit_annotations.csv --run-id reviewed-pilot-001
```

`compare` optionally accepts `--split /path/to/frozen-split.json` with `development` and `holdout` group ID lists. Keep run IDs unique. For scoring with an evaluated selected learner, use `score --scorer ridge --model-version reviewed-pilot-001` (or xgboost only if that candidate was selected/evaluated), with compatible request versions. No command provisions a RunPod resource or trains during scoring.

## Completion gates and limitations

| Gate | Actual status | Evidence |
| --- | --- | --- |
| A — math/contracts | passed | Focused checks verify scales/weights, 0/100/67 baseline cases, monotonicity, unknown/zero handling, effort ranges, combination bounds, low scores and consistent missing-market behavior. |
| B — CPU learner machinery | pending | Code delivered for both learners, timings, save/reload tolerance 1e-9 and smoke isolation. No verified RunPod execution available. Local Ridge construction succeeded; local XGBoost import failed for missing libomp. No fit/predict/reload timing is claimed. |
| C — empirical agreement | not_evaluated | Both supplied/new annotation templates have zero data rows and zero profile groups. Reviewed milestone catalogue and independent labels are absent. No real split or empirical ranking/error metrics exist. |
| D — application boundary | passed | Default service/CLI returns a schema-valid baseline result (67); unavailable learners, missing information, horizon mismatch and disabled LLM behavior are tested. This is callable integration, not an HTTP/API deployment claim. |

The 32-row synthetic mathematical fixture exists only for future smoke execution. The grouped-control-flow test uses stubbed fitting/persistence and fictional annotation provenance in temporary storage; it tests split/selection/holdout control flow, not Ridge/XGBoost or label agreement. The dependency-free test run initially skipped JSON schema validation; the installed-environment run includes it. See the evidence JSON for the final exact test count and actual commands.

Per-candidate fit duration, inference timing, reload equality and empirical NDCG/MAE are **unmeasured** for Ridge and XGBoost until the authorized runner and reviewed data are available. There are no training/holdout rows to count today: 0/0, with no real split created. The baseline remains the default until genuine grouped comparisons, holdout diagnostics, counterfactual review and team acceptance justify an explicit learner configuration. Even a successful pilot measures rubric agreement, not real-world career effectiveness.

Implementation was authored with Codex assistance. It uses declared third-party library APIs; no pretrained weights, scraped labels, hosted LLM calls or existing source-pack bytes were introduced or modified by this task. Preserve source-pack attribution and record actual RunPod usage in the team's declaration only when it occurs.

Primary API references consulted: [Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html), [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html), [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html), and [trusted model persistence](https://scikit-learn.org/stable/model_persistence.html). Actual resolved local versions are recorded in the evidence rather than assumed from current documentation.
