# Fictional market scenario experiment — data and model card

**Simulated scenario — generated assumptions, not observed Malaysian demand.** Datasets, prediction exports and model metadata retain this label and `synthetic=true`; dataset/model metadata also explicitly set `normal_serving_eligible=false`. This is an isolated experiment, with no new end-user simulation mode.

Purpose: exercise count forecasting under specified assumptions, measure baseline/Ridge/XGBoost behaviour, demonstrate clean splits and prepare a reproducible bounded worker job. It does not fill missing Malaysian observations, estimate coverage for personal-only roles, validate career suitability or establish augmentation benefit.

## Data and label lineage

`fictional-market-scenarios-v1`, seed **20261023**, generates **864 records**, **18 fictional role/skill series**, **9 whole scenario/source groups**, over **48 simulated quarters (2010–2021)**. These are scenario counts, not additional observed source coverage. Units are fictional advertisement counts; geography is explicitly `SIMULATED`. No real aggregate anchors, restricted records, CVs, user profiles or LLM-generated labels are used. The generator is fixed equations and bounded random noise, without data fitting/calibration.

The spec fixes stable, rising, falling, seasonal, abrupt, sparse, missing-period and changed-coverage scenarios, plus an unused damped-cycle robustness family. Role/skill pairs are deliberately correlated: skill counts are approximately 55% of role counts plus bounded noise, capped at role counts. They always share a split. The rising equation reuses the existing test generator's `10 + 2*i + 3*(i%4)` assumption. Existing feature, estimator, prediction and metric code is reused rather than replaced.

There are **8 missing cells** and **72 generated zero cells** across the full dataset. Missing history/targets are excluded, never filled with zero. Coverage changes create a new source-universe ID and denominator; features never bridge epochs. Latest four contiguous known quarters form lag/change/seasonal-calendar features. Simulated publication occurs 20 days after quarter end. Prediction is for the next calendar quarter from issue time: a **two-quarter lead from the latest observation**, not a current real-world forecast.

Dataset SHA-256: `b7aa327d30220b27a2236476b5c51d45d04deb16d9bfb009cc2fcca81a01880b`.

## Splits and fits

Complete scenario families are assigned before random draws: stable/rising/falling train; seasonal/sparse validation; abrupt/missing/coverage-change test; damped-cycle robustness only. No correlated pair or variant crosses a family/source split. Training labels must be published before 2018; validation issues are 2018–2019 with labels published before 2020; test/robustness issues are 2020 onward. This leaves **156 train, 24 validation, 34 test and 14 robustness examples**, half in each output family. Held series' own past observations are legitimate prediction context, never training labels.

For each role/skill output family, the same eligible examples compare last-value and seasonal baselines, train-only standardized Ridge (alphas 1/10/100), and XGBoost (depths 2/3, 48 trees, learning rate .05, one CPU worker). Parameters and method choice use validation MAE only; ties prefer the simpler declared method order. Selection is written before any test predictions. No validation/test refit occurs. Two pilot fits plus ten full candidate fits give **12 fits per run**, bounded by 120 seconds between fit checks. Three deliberate local executions were performed: original measurement, clean-checkout reproduction, and job-launcher end-to-end verification (**36 synthetic experiment fits**, including six pilot fits; separate unit-test smoke fits are not counted in this experiment total). These are reproductions of one frozen experiment, not three independent evaluations or a repeated search.

## Measured outcomes

Final test MAE, in fictional advertisement counts, **17 examples per output family**:

| Method | Role | Skill |
| --- | ---: | ---: |
| Last value | 1.4706 | 1.5294 |
| Seasonal | 2.1765 | 1.8824 |
| Ridge | 10.4692 | 5.7879 |
| XGBoost | 29.0250 | 15.7132 |

Seasonal was the frozen validation choice for both families. Last value performed better on the final test; this did not trigger reselection. On the additional damped-cycle family (seven examples per output family), MAE was **7.0000/3.7143** for last value, **11.1429/6.0000** for seasonal, **7.1561/4.1704** for Ridge and **6.3293/3.6723** for XGBoost (role/skill). This demonstrates sensitivity to assumptions, not a universal model winner.

`synthetic-results.v1.json` contains MAE, RMSE, WAPE, sample counts and zero counts per split and scenario, all parameter trials and artifact lineage. WAPE is an absolute-error ratio, null if actual total is zero. Sparse zero outcomes occur in validation; final test has no zero labels. Train scenario metrics are explicitly labelled resubstitution. The abrupt shift occurs in 2018, so the final test evaluates a sustained unseen regime, not the immediate shock. Coverage changes in 2017; its test uses only the new epoch. Short test slices and assumed equations limit conclusions. No calibrated uncertainty or ranking accuracy is claimed.

Original local CPU training took **0.1383 seconds**, excluding interpreter/import startup, with process peak RSS **126.48 MiB** including imports. The 16-example pilot took **0.0187 seconds**, peak RSS **123.11 MiB**. These are local measurements, not provider runtime/cost guarantees. Python 3.9.6 and exact package versions are recorded. A clean code checkout with no original raw inputs reproduced the dataset, predictions and all metrics exactly; Linux/RunPod equivalence has not been measured. The worker launcher checks metric agreement to absolute tolerance 1e-5.

## Serving and evidence boundary

Eight artifact exports per run (two families × four methods, including baseline placeholders) remain under ignored synthetic-lab paths. Metadata ties each to dataset/code hashes, method/parameter, training example IDs, features and environment. Nothing is registered in the normal loader. Normal market evidence service, observed-data experiment runner and forecast registry reject the synthetic dataset/manifest; unchanged observed hashes and empty selected-model registry are verified.

Normal current evidence still comes from the 155-requisition Bosch sample, explicit DOSM published offering facts and MyCOL source-coded shortage context, with the measurement/reuse limits in `HANDOFF.v3.md`. Its counts are unchanged. **No synthetic-only model is selected for normal runtime. Real role and skill forecasts and independent real validation remain unavailable**, because comparable deduplicated historical quarterly targets and publication vintages are absent. No real-only versus augmented-data evaluation exists. A's personal recommendation policy is untouched.

## RunPod status and submission paragraph

`synthetic-runpod-job.v1.json`, its pinned requirements and `checks/run_synthetic_job.py` define the CPU-only worker. The launcher was executed successfully locally from the clean checkout and does not provision resources. No RunPod job ran: job ID null, session paid cost **USD0**, remaining credits unknown. No configured key/token/private config was found. A verified image, quote, prior jobs/balance, external termination and separately authorised bounded launch remain prerequisites; Git publication authority does not grant spend.

Submission wording: “Minder uses Bosch employer advertisements, DOSM published job-offering statistics and MyCOL shortage designations for current Malaysian market context within their stated scope. Separately, fictional-market-scenarios-v1 generated 864 fictional aggregate records across nine scenario families to evaluate forecasting machinery. Last-value and seasonal baselines, Ridge and XGBoost were compared using disjoint family/source groups, chronological boundaries and validation-only tuning. Results measure performance under generated assumptions, not real Malaysian forecast accuracy. Real role and skill forecasts remain unavailable because compatible historical advertisement targets and publication vintages are missing. Experiments ran locally; no RunPod training or synthetic model activation is claimed.”
