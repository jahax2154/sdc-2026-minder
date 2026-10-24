# Minder dataset and scoring starter pack

Prepared 20 October 2026. This pack contains real downloaded reference datasets, source metadata and a proposed numerical design. It contains no trained personal model, no invented personal outcome labels, and no validated two- or five-year labour forecast.

## Start here tonight

1. Read sources_manifest.json before joining files. It records source URLs, retrieval times, original units, byte hashes, observed dates, versions, and limitations.
2. Choose the eight career roles and review their skill requirements. Use O*NET as a role reference, and create user-facing initial skill targets using one consistent task-anchored rubric. The downloaded ESCO crosswalk is old and includes multiple relation types; review candidate mappings rather than joining blindly.
3. Read scoring_spec.json. F is personal preparation fit; D is market assessment; S is a decision-policy combination. Only factor weights sum to one. F and D each range independently from zero to100. Missing evidence remains unknown.
4. Populate templates/personal_fit_annotations.csv using genuinely varied profiles and human-reviewed grades. The file intentionally contains a header only. Market attractiveness must not influence these grades because it is added separately by policy.
5. Freeze profile_group_id splits before modelling. Keep related synthetic profile variants together. Train a transparent baseline and Ridge, then compare one shallow boosted-tree model only if time permits.
6. Validate F against personal-fit grades. Validate S separately against policy scenarios or market-aware judgement labels. Save the preprocessing and schema with the model.

## What the source files support

- DOSM Job Market Insights: an official Excel workbook of national online job offerings by economic activity and by major occupation group. The derived long table contains 952 rows across 28 quarters, 2019Q3–2026Q2: 921 numeric observations and 31 missing values. These are two separate marginal tables, not joint industry-by-occupation or state-by-role data.
- DOSM occupation wages:480 rows,2010–2025, nine occupation major groups plus overall. Nominal RM/month and recipients in thousands. Broad context, not detailed technology-role demand.
- DOSM state wages:816 rows,2010–2025, state/national marginals. Do not join with the occupation table and claim observed occupation-by-state wages.
- DOSM state labour force:608 rows,2017Q1–2026Q2. State-wide labour force and unemployment, not occupation-specific demand.
- O*NET31.0 occupation, essential-skills, software-skills and scale-reference tables. These describe U.S. occupations; many measurement dates predate the database release. Importance1–5 and Level0–7 are distinct scales.
- ESCO–O*NET crosswalk:4,253 mapping records after16 metadata lines. Read with skiprows=16. Source mapping versions are O*NET-SOC2019 and ESCOv1.1.0, not current taxonomy releases. Exact, broad, close and narrow matches are distinct.
- ILO author workbook:3,265 task rows with repeated occupation summaries. derived/ilo_genai_occupation_2025.csv preserves the published summary once for each of427 occupation codes. Technical AI exposure is not a demand forecast. Task standard deviation is task variation, not forecasting uncertainty.

Preserve occupation identifiers as strings, including leading zeros. Preserve suppression/relevance flags and original geographic scope. A reference dataset release date is not every row's measurement date. Present sources at the actual available granularity.

The latest Job Market Insights economic-activity table needs a coverage review before interpreting sector growth: Unclassified offerings rise from 49,549 in 2026Q1 to 273,024 in 2026Q2, out of a latest total of 555,509. This does not establish why the classification changed. Preserve the unclassified share and avoid explaining classified-sector declines as economic deterioration without further evidence. Annual 2026 totals are partial-year. The historical columns are the current release vintage, not an archive of historical publication vintages.

## Still needed for a trained recommendation model

- User profiles or explicitly synthetic test profiles.
- A reviewed eight-role skill/initial-preparation catalogue.
- Independent relevance annotations for each user-role pair, with a clear horizon and rubric.
- A task catalogue with prerequisites, estimated effort ranges, evidence links and completion criteria.

## Still needed for actual future demand forecasting

A comparable role-by-geography-by-time panel of demand observations and historical feature snapshots. The acquired Job Market Insights history supports broad national analysis and possible carefully scoped forecast experiments, but does not supply narrow career-role or state-by-role histories. Each training example must pair evidence genuinely available at cutoff t with an observed outcome at t+h; all training outcomes must be available before the test forecast origin. Employment stocks, job postings, vacancies and hires are different measurements. Do not fill this gap by turning news sentiment or LLM opinions into claimed ground-truth demand labels.

Two years means eight quarterly steps and five years means twenty. Twenty-eight quarters provide very limited long-horizon evaluation. In particular, this dataset alone cannot support a conventional direct five-year model backtest with completed training outcomes available before the test origin and completed test outcomes also in the dataset. Producing an extrapolation is easier than validating it.

For the first prototype, use dated current evidence and explicitly labelled future scenarios. If D cannot yet be computed fairly across all candidate roles, rank the comparison set by F and keep D/S null, with market evidence shown alongside.

## Files and verification

- raw/:11 original downloads; no changes to downloaded bytes.
- derived/:verified occupation-level ILO summaries and the DOSM quarterly job-offerings table, with source IDs and source-cell provenance for DOSM.
- sources_manifest.json:provenance, hashes, original schemas and limitations, plus source links not downloaded.
- scoring_spec.json:proposed meanings, equations, missingness and validation decisions.
- templates/personal_fit_record.schema.json:proposed row schema.
- templates/personal_fit_annotations.csv:empty annotation template.
- math_checks.json:arithmetic convex-combination checks only. These are not empirical model-quality results.

Use each source under its stated terms and retain attribution. The specific ESCO crosswalk file's reuse licence was not independently verified; its public source is recorded for review. No paid API calls, RunPod resources, or user data were used in constructing this pack.

