# Minder Phase 2 — APPROVED DATA ENGINEERING HANDOFF

**Status:** Approved to begin engineering from 2026-10-21. This is a *schema and pipeline approval*, **not** approval of any individual role requirements, labels, source mapping, skill-demand values, or country-level comparisons.

## Context to preserve
- Existing monorepo: extend `ml/src/minder_ml/intelligence/`, existing review worksheets (`ml/data/review/`), and checks (`ml/evaluation/continuation_checks.json`). Inspect structure and `AGENTS.md` before writing files. Do not create a parallel intelligence stack.
- Existing foundation: fixed personal-fit baseline, Ridge, XGBoost CPU paths; known mathematical fixture = 67. Do not claim any empirical validation or fitted models. OpenMP imports work but RunPod fit/predict/save/reload and reviewed-label evaluation remain pending.
- Three proposed role cards, six criteria worksheets, 24 source-mapping candidates: **pending substantive review**.
- Zero reviewed profile–role labels; no meaningful raw profile has been supplied. User-profile and role-catalogue **schemas are approved**.
- Separate `personal_fit` from `market_evidence` and from the `overall_recommendation_index`. Personal-fit means alignment and feasible *initial preparation*, not probability of getting a job or probability of long-term career success.
- User wants quarter/country/region, role, skill, industry, and optional employer breakdowns, with one reusable data-engineering framework. Implement only dimensions supported by each source.
- Do not automatically retrain on every market update; recompute derived indicators and version snapshots. Model retraining only through a separately evaluated training workflow when suitable labels/outcomes and a justified need exist.

## Start now — required outputs (no additional approval needed to write code)

### 1. Define canonical data entities
Implement validated schemas and null-handling for:
- `UserProfile`: id, version, synthetic/private marker, profile_family_id, career_goal, country/region preference, planning_horizon, hours/week, skill observations with `assessed/self_reported/demonstrated/unknown`, interests, projects/achievements, education/experience, work preferences, access/budget constraints. Never persist actual secrets or sensitive identifying profiles into public training fixtures.
- `RoleDefinition`: stable role_id, role title, preparation milestone, role task/interest tags, required `criterion_id`/`skill_id`/importance and observable evidence rule, mapped occupation identifiers with taxonomy version and review status, sources and reviewer provenance. Allow *pending* records; only approved records may support authoritative scores.
- `PersonalFitAnnotation`: profile_id, role_id, rubric_version, preparation_horizon, grade {0,1,2}, reviewer_id, rationale, review_status, profile_family_id, label_source (`human_reviewed` or `weak_auto_proposal`). User accepting a role is **not** a positive ground-truth label.
- `MarketObservation`: source_id/version, indicator_id, value/unit/denominator if relevant, geography_code/level, period_start/end/frequency, available_at/publication/retrieval dates, taxonomy system/version and role code where present, optional skill_id / employer_id / industry_id, population/source coverage, measurement method/version, `observed|estimate|scenario|forecast`, data quality status.
- `RoleMarketCrosswalk` and `SkillTaxonomyCrosswalk`: identifiers, from/to taxonomies and versions, scope, mapping type, source, review_status, reviewer notes.

### 2. Build one canonical observation table; expose THREE supported views
Do not build an enormous, fully populated geography × quarter × role × skill × employer tensor. It will be sparse and would invite invented values. Store long-form observations with explicit null dimensions and generate:
- `role_market_view`: (source, geography, period, occupation) + observed offering counts, share, comparable growth, source metadata;
- `skill_market_view`: (source, geography, period, skill[, occupation]) + observed skill mention/count/share **ONLY when verified skill-tagged posting data is acquired**;
- `employer_market_view`: (source, geography, period, employer[, occupation]) + employer posting activity **ONLY when an authorized, properly attributed employer-level source is acquired**.

Do not call employer posting activity the company's hiring volume, nor ESCO occupation-skill associations current measured skill demand. Missing views must report `not_supported_by_sources`, not zeros.

### 3. Implement comparability keys and rejection rules
Two observations are directly comparable only when the target metric is the same, units/denominator have the same meaning, population/source coverage and methodology are compatible, occupation/skill classification and versions are suitably mapped, geography relates to the comparison being made, and observation windows are aligned. Preserve methodological discontinuities and missing quarters. Do not convert annual data to invented quarters. For cross-country comparisons, do not compare raw online posting counts from differently covered providers as national market sizes; preserve source coverage and normalization choices. Industry totals and occupation totals are different marginals, not joint records.

- Safe derived YoY change: `100 * (value_t / value_t_minus_4 - 1)` for positive denominator and comparable quarterly series.
- Safe observed source share: `value / observed_total` only if same source/window/population and denominator recorded.
- No min/max 'hotness' ranking across arbitrary countries/sources, no 'AI job growth forecast' from ILO exposure.
- Market rankings start as **indicator-specific, within a comparable cohort** (e.g., observed job-ad count or YoY movement) with date/scope labels. A scalar weighted market score policy is **not yet approved or empirically calibrated**; add behind an explicit policy version only after review.

### 4. Data ingestion + repeatability
Inspect actual checked-in source pack before mapping columns. Keep original source bytes immutable and hash them; source-specific parsers (start with the existing DOSM quarterly job-offering material); canonical clean rows; data-quality checks; derived views; source and review manifests; versioned snapshots. A rerun with identical sources/configuration should yield equivalent canonical records and metrics. A new release creates a new version and does not overwrite frozen training or holdout rows. A source refresh must not trigger model training.

Expose/reuse CLI commands (follow repository conventions):
```
minder-data inspect
minder-data prepare
minder-data validate
minder-data market-build
minder-data annotation-export
minder-data report
```
If command packaging is not yet present, implement equivalent Python module commands and document exact invocations. Do not create an additional service.

### 5. Human-in-the-loop labelling, not 200 manual entries
- Prepare profile-generation **templates**, optionally generate diverse labelled-as-synthetic draft profiles. Do not call them reviewed examples automatically.
- Generate user–role pairs and precompute features/gaps without displaying baseline scores to human reviewers.
- Implement **blind annotation export/import** with role requirements, relevant profile evidence, rubric 0/1/2, rationale, and reviewer ID.
- Optionally produce machine/LLM suggested labels into a separate `weak_auto_proposal` file; do not merge into human-reviewed ground truth or held-out evaluation. If no API credentials, skip automatic LLM labelling without blocking.
- Review a small calibration batch (e.g., 5 profiles × 3 roles), establish agreement and resolve ambiguous rubric definitions; then expand to ~25 independent profile families × 8 roles if review capacity permits. For evaluation, hold out complete profile families. No accuracy claim with only weak labels.
- Aggregate review counts, disagreements, and unresolved cases in readiness reports. Do not invent reviewer names or mark approvals based on script assertions.

### 6. Vertical slice + safety behavior
Use existing five-feature baseline and feature builder. Provide a deterministic, clearly synthetic example profile for **software smoke tests only**. Only run meaningful baseline role comparisons once the corresponding requirement cards have been approved. On missing assessed criteria return explicit `insufficient_information`. Preserve per-criterion gaps and source IDs. Keep individual data absent from public repo artifacts.

### 7. Gates, with actual evidence (mark BLOCKED, not PASSED, where data absent)
- **P2-0 Contract:** approved schemas and canonical enums implemented, versioned; schema/validation tests PASS.
- **P2-1 Source ingestion:** real DOSM material parsed; immutable source checksum and provenance; observed metrics round-trip; methodology exceptions logged.
- **P2-2 Comparability:** one permitted within-series comparison and one rejected incompatible pair; annual/quarter mismatch and cross-country coverage mismatch rejected.
- **P2-3 Review readiness:** 3 role cards available with `pending` until human-approved; blind review export/import works; exact counts of approved roles, profile families, and gold labels.
- **P2-4 Baseline meaningful inference:** 1 supplied or explicitly synthetic profile × 3 *approved* roles -> validated five features (or explicit missing reasons), per-criterion gaps, baseline rank.
- **P2-5 Repeatability/integration:** rerun same snapshot deterministically; preserve trained/frozen-holdout assets; JSON interface remains backward compatible with current scoring service and frontend contract.

After each run, return gate result, actual command and environment, validated/rejected row counts, source dates, visible blockers and recommended next steps. Do not claim any learner training, generalization, time-series forecast, company ranking or observed skill-demand ranking unless the required evidence exists.

## Non-goals
No new LLM provider, fine-tuning, model retraining, international country data scraping, silent market-score imputation, demographic-based suitability scoring, or reimplementation of the existing foundation. Do not wait for missing reviews to implement approved schemas, ETL, validators, CLI and annotation packets.

## Evidence references to retain in source notes
- DOSM Q2 2026 Job Market Insights: https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026
- OECD online-posting comparability research: https://www.oecd.org/en/publications/how-well-do-online-job-postings-match-national-sources-in-large-english-speaking-countries_c17cae09-en.html
- ESCO downloads: https://esco.ec.europa.eu/en/use-esco/download

## Final instruction to Codex
Implement the highest-value unblocked tasks now. Do not ask to approve the already-approved V1 schemas. Do not silently approve occupational content, ratings or annotations. If raw data is missing, report it precisely, retain source provenance, and continue on validators, worksheets, adapters and tests. Commit/push only under existing repo workflow and explicit user permissions.
