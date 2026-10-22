# Minder ML design

## Status and ownership

**Design status: PROPOSED. Implementation evidence: not inspected or verified in this update.** No model, training run, evaluation result, or deployed ML service is claimed by this document.

[PRD.md](../PRD.md) owns product requirements, scope, and hackathon rules. [ARCHITECTURE.md](ARCHITECTURE.md) owns system boundaries and the [API contract](ARCHITECTURE.md#api-contract). [DATA_SOURCES.md](DATA_SOURCES.md) owns candidate sources and provenance. Change those documents when their decisions change; do not create competing requirements here.

Use the [shared status definitions](../README.md#current-status). Design agreement and implementation verification are separate; retain actual checks and results before marking a model verified.

The **20–30 hours of ML effort** and **US$25 preliminary-round RunPod credit** are confirmed planning constraints. They do not guarantee GPU hours, enough labelled data, or a particular model's feasibility. The technology stack, model, labels, selected dataset, geography, role count, and prediction horizon all remain **OPEN**.

## Proposed learning problem

Investigate **profile-to-role relevance first**: given an explicitly supplied profile and a reviewed set of roles, order roles by a defined relevance rubric and explain the supporting evidence. The rubric, required profile information, supported roles, and meaning of a useful recommendation need agreement before training.

A ranking index expresses relative relevance under that rubric. It must not be presented as a probability of career success, employability, salary growth, or getting hired. Research about occupational exposure to AI must not become a personal job-loss probability. Demand evidence and exposure context need their own dates, geography, and qualifications; combining them into a score requires a documented decision.

Do not add a forecast merely because a source contains dates. A prediction horizon and any forecasting task remain OPEN. Requirements for course recommendations and SDG claims remain in the PRD; they are not inferred from the presence of a model.

## Proposed inputs and outputs

| Input family | Intended information | Decision needed |
|---|---|---|
| Profile | Supplied skills, experience, interests and practical constraints | Accepted fields, missing-value handling and skill-level interpretation |
| Role catalogue | Real role IDs, definitions and required/relevant skills | Supported roles and reviewed cross-source mappings |
| Dated signals | Relevant market or AI evidence with time, geography and units | Which signals justify role-level conclusions |
| Scenario | Explicit assumptions applied to the same profile/evidence | Scenario definitions and allowed transformations |
| Learning resources | Verified resources associated with gaps | Prerequisites, cost and effort estimates |
| Evaluation labels | Independent relevance judgments under a stated rubric | Label source, rubric and reviewer agreement |

The engine should produce ordered roles, explained scores and skill gaps; pathway rules use those gaps to order reviewed resources. Preserve evidence and version references. Exact response structures are owned by the API contract, not a second schema here. LLM explanations must stay consistent with these structured outputs.

## Baseline before a trainable candidate

The proposed sequence is an inspectable baseline, an evaluation setup, and then a simple trainable candidate only if the available evidence justifies one. The baseline method and any weights are OPEN. Its inputs must come from reviewed profile fields and sources whose use is justified.

**PROPOSED baseline:** transparent skill-coverage and interest-fit components, with explicit handling of user constraints. Keep trend/scenario evidence separately explainable; decide whether and how it changes ordering before combining it into a score. No weights or score scale are fixed here.

Use the baseline to expose missing data, ambiguous role mappings, and integration problems. Keep it available for comparison. One candidate worth evaluating after labels exist is a small regularised linear model for rubric-based relevance. That is a proposal, not a selected algorithm. Adopt a trainable model only if it addresses a defined weakness on the same held-out examples; record the eventual model choice and rationale here.

Allocate the time budget across preparation, label review, evaluation, integration, and documentation. Estimate actual runtime and cost before any experiment. Follow the PRD's tool rules: **any GPU work belongs on RunPod**; CPU smoke validation may run elsewhere. No experiment has been executed in this documentation update.

## Labels and evaluation

The target label and its provenance are OPEN. Before fitting a candidate, define what a reviewer is judging, what evidence they can use, how disagreements are resolved, and what would make the label unreliable. A relevance judgment is different from a measured employment outcome.

Synthetic profiles and labels can exercise the workflow. Labels generated by the same baseline or assistant being evaluated primarily measure imitation or consistency. They do not establish independent recommendation quality. Record synthetic provenance explicitly and keep claims within that limit. If independent labels are unavailable, retain the baseline and report that limitation instead of inventing an accuracy claim.

Use a **grouped holdout by profile or originating template**. Keep variants of the same profile/template together so that near-duplicate examples cannot appear on both sides of the split. Splitting individual profile–role pairs at random can leak profile information. Freeze the evaluation set before tuning; document any later replacement.

Choose the relevance metric, comparison procedure, and acceptance threshold after the label task is defined. No score is reported yet. Compare candidate and baseline on identical cases, inspect disagreements, and include sparse profiles, missing evidence, unknown roles, and ambiguous mappings. Separate offline relevance evidence from successful API integration and from real user outcomes.

## Shared transformations and versioned evidence

Training and serving must use the same versioned interpretation of profile fields, role identifiers, missing values, and transformations. Fit any learned preprocessing only on the training partition. A serving shortcut that changes those transformations invalidates the comparison until checked. See [scikit-learn's guidance on data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

For an eventual experiment, retain a reviewable record of:

- Source snapshots and the provenance manifest, including any permitted derived data.
- Label rubric, label provenance, grouped split membership, and known limitations.
- Code revision and transformation/configuration versions.
- Baseline and candidate identifiers, evaluation procedure, and actual measured results.
- Artifact checksum and compatible input/output contract version; runtime and cost if an experiment occurs.

These are required evidence categories, not a final file format or schema. Store no secret values in artifacts. Keep large artifacts outside ordinary source history and provide an accessible retrieval reference when an artifact exists.

**Pretrained-model declaration: OPEN; none selected here.** For any eventual pretrained model or embedding service, record provider, exact model/version, official reference, licence/terms, intended use, modifications and attribution. Include its actual use in the final tools/IP declaration; do not infer a licence from availability.

## Serving and fallback

Keep the model behind the interface defined in the [API contract](ARCHITECTURE.md#api-contract). Propose contract changes there instead of introducing local response fields. Serving location and CPU/GPU requirements remain OPEN; the RunPod rule applies whenever GPU execution is used.

An unavailable or rejected model may use a verified baseline only when that path is explicitly identified to the caller and user according to the shared contract. Do not silently describe baseline output as trained-model output. If no valid baseline or supporting data is available, return the agreed unavailable state rather than manufactured rankings.

For a baseline implementation, verify its transformations, documented behaviour and an end-to-end request through the real integration boundary. For trained-model serving, also demonstrate compatible artifact loading and the agreed candidate-versus-baseline evaluation. Record limitations alongside results. Successful inference proves the path runs; it does not prove career benefit.

## Authorized foundation implementation — 20 October 2026

The later [execution task](ml/docs/MINDER_ML_FOUNDATION_CODEX_TASK.txt) fixes the foundation's five-feature rubric, baseline weights, Ridge and CPU XGBoost candidates, score mapping and grouped evaluation procedure. It supersedes the OPEN algorithm details above for this bounded task only. [Foundation implementation and evidence](docs/ml-foundation.md) records the actual code, commands, gates and limitations. Baseline remains the default. Recorded fitting requires verified RunPod CPU execution under this task's stricter instruction, despite the earlier broader CPU allowance. No reviewed labels or reviewed milestone catalogue were supplied; no career-effectiveness or model-improvement claim is made.
