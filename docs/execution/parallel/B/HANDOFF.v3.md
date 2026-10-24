# Session B — current Malaysian coverage expansion

This B3.2-R02 handoff supersedes the current-coverage sections of v2. Earlier reports remain historical evidence. Branch: `session/b-market`. No recovery, acquisition of already pinned DOSM inputs, or completed training phases were repeated.

| Phase/refinement | Status | Delivered behaviour | Checkpoint |
| --- | --- | --- | --- |
| B1.1-R04 | limited | Official-source comparison, per-record reconciliation with A, 96 callable source facts | `f9dcd93577aff3d4e2da02164ec06bb31b445338` |
| B1.1-R05 | passed | 43 explicit six-digit memberships within four MyCOL groups; unlisted children stay unknown | `ba469e426284b1def8a95474e64c90b8aeb95f9a` |
| B3.2-R02 | limited | Final verification and this integration handoff; remaining integration/reuse limits stated | Commit containing this handoff and `B3.2-R02.json` |
| B1.2 / B3.1 | already_satisfied | Current/forecast interfaces and checked packaged loader retained | Prior checkpoints in `HANDOFF.v2.md` |
| B2.1-R02 | already_satisfied | Publication-aware eligibility and baseline/Ridge/XGBoost implementation retained | `db06fedf593d3e448d1e2c9a3d77b52703bb0e06` |
| B2.2-R01 | deferred_dependency | Real runner found zero eligible approved-target examples; no real fits, evaluations or selected models | `ff4036eaef04a9164afb936784ba682c69d018be` |

Final relevant suite: **51 tests passed in 22.399 seconds**, with RuntimeWarnings treated as errors. This covers market service, forecasting machinery and shared service contracts. The current-context snapshot hash matches the serving registry. All 13 bootstrap inputs still match their pinned hashes and have no writable mode bits. All 68 changed paths from bootstrap through R05 are B-owned. The final documentation paths are also B-owned. Detailed hashes/checks are in `B3.2-R02.json`; local raw logs remain excluded.

## Reconciliation with A

`CURRENT_COVERAGE_RECONCILIATION.v1.json` pins the inspected committed A report and classifies every one of the **35** official role-label observations. A's four already integrated market-informed roles remain Accountants and Auditors **0**, Software Developers **5**, Data Scientists **0**, Industrial Engineers **0**, within the **155-requisition Bosch sample**. These are the existing provisional employer-title rules and exact O*NET identity aliases, not an official MASCO crosswalk. Sample zeros say nothing about national low demand.

The **five Q2 2026** official observations are already callable as source-label facts and await occupation-code mapping for canonical use. The **30 older** observations are historical context. All 35 are unsuitable for A's Bosch count comparison: different platform universe, period and offering measure; unverified unique-ad/positions equivalence; no verified occupation codes in those extracted entries. Missing top-list entries are unknown, never zero. The reconciliation also records exact reasons for treating the frozen JobStreet corpus and other reference sources as historical/context-only.

## Actual delivered breadth

| Evidence family | Delivered breadth | Meaning and limits |
| --- | --- | --- |
| MyCOL 2024/2025 | **66 distinct MASCO 2020 four-digit groups** | National occupation-shortage designations, not advertisement volume or a rank. The report declares 18 study sectors, without a per-occupation sector join. |
| Verified MyCOL detail | **43 explicit six-digit memberships within 4 of the 66 groups** | Groups 2141, 2411, 2512, 2524; profile pages 79, 113, 125, 137. Nominated-job-title restrictions retained. Other child scopes remain unverified. Do not add hierarchical counts together. |
| DOSM Q2 2026 | **21 distinct economic-activity labels; 9 major occupation groups** | Dated published offering levels, not joint occupation-sector cells or narrow-role/skill counts. Workbook-native missing codes remain null. |
| Existing employer observations | **1 identified employer feed, 155 native requisitions** | Native-ID deduplicated, provenance retained. 154 qualification sections; one missing. The old 40 limit was the collector default; the remaining 115 were acquired previously. |
| Official role-label facts | **35 observations across 7 labels**, including 5 latest observations | Separate source-native facts; not 35 distinct occupations or canonical count mappings. |
| Galaxy inspection | **3,041 six-digit codes; 428 four-digit prefixes; 21 sector codes inspected locally** | **Zero bulk records distributed**. Do not count inspected-but-held data as application coverage or sum per-occupation employer counts. |

There is no cross-taxonomy distinct-occupation grand total. No identified employer was added by this institutional expansion. DOSM and MyCOL do not provide a deduplicated employer denominator for these facts. Observed advertisement activity does not represent the entire Malaysian employment market.

MyCOL's exact publication date and continuous fieldwork interval were not verified: relevant date fields stay null, with the 2024/2025 edition and mixed statistical/survey basis explicit. Retrieval is not the observation date. DOSM Q2 covers 1 April–30 June 2026 and was published 18 August 2026. Its source total of 555,509 includes 273,024 economically unclassified offerings; classification/coverage review flags prevent unsupported growth comparisons or narrow-role allocation.

## A integration surface

Integrate R04 followed by R05 and this checkpoint. Runtime needs only committed JSON and existing Python code; local PDF/OCR acquisition tools are not new runtime dependencies.

```python
from minder_ml.intelligence.market_service import MarketEvidenceService

market = MarketEvidenceService()
context = market.current_context(
    as_of=issue_time,
    occupation_system="MASCO", occupation_version="2020",
    occupation_code="2512-01",
)
```

Use an explicit source-native code or selected evidence IDs; see actual outputs in `current-context-examples.v2.json`. An enumerated child returns its parent fact plus separate query-scope/source-page provenance. It does not create a child title, canonical O*NET mapping or personal score. `current_context_catalogue` supplies dated native labels/codes for discovery. Existing `current`, `forecast` and `published_role_observations` remain separate.

A owns consuming this additive versioned context envelope and any shared DTO or canonical crosswalk. B requests context integration, preserving measurement/date/source/limits, through `requests/B-to-A-contracts.md`. No shared schema, root dependency, backend or UI path was edited. A's existing numerical count comparator must not treat a shortage designation or a DOSM marginal as another Bosch advertisement count. Original N01 remains pending; A's separately documented provisional policy is not represented as N01 approval.

## Sources, reuse and privacy

`OFFICIAL_SOURCE_COMPARISON.v1.json` records the requested official URLs, source conditions and acquisition hashes. The [MyCOL report](https://www.talentcorp.com.my/images/uploads/publication/204/MyMahir-Malaysia-Critical-Occupations-List-MyCOL20242025-1773385490.pdf) was acquired and its national table and selected profile code blocks inspected. Derived facts contain codes/designations with attribution, not copied report prose; an open licence is not asserted. The [DOSM Q2 release](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026) and pinned workbook were reused.

The [official Galaxy entry](https://myfuturejobs.gov.my/bm/myfuturejobsgalaxy-2/) and its public occupation/aggregate responses were inspected. Its linked [terms](https://myfuturejobs.gov.my/wp-content/uploads/2024/03/TermsAndConditions.pdf), clauses 4.3/4.4, restrict storage/reproduction/distribution; no separate open-data permission was located. Bulk application redistribution remains held. The displayed aggregate notes name April 2026, while per-record publication/observation dates are not supplied. No permission or contemporaneous national coverage is inferred.

Only public aggregate and occupational information was requested. No candidate routes, CVs, applicant profiles or recruiter-contact endpoints were requested; incidental contacts in source documents are excluded from derived data and LLM inputs. Derived records use an aggregate-field allowlist, with contact stripping; the final derived-context email scan found none. Raw documents, OCR and source responses remain local under ignored B artifacts, outside application/LLM payloads. These, local pypdf/tool caches and run logs have no new external backup. The original 13 read-only source inputs remain untracked in their existing G0 snapshot; no credentials, database, model weights or unrelated files were staged.

## Remaining dependencies and costs

Current native context is delivered now; A consumer integration and code-backed canonical joins remain. Galaxy bulk reuse requires applicable permission. Neither blocks the delivered MyCOL/DOSM context.

Comparable historical quarterly Malaysian unique-ad counts for each approved role and advertisements requesting each skill, with stable source/taxonomy/deduplication and publication vintages, remain missing. DOSM's 28-quarter broad marginals cannot supply either narrow target. The prior 69,024-record frozen corpus has incomplete quarters and availability/coverage gaps; it was not relabelled as valid forecast history. No different-target broad-industry experiment is presented as approved-target evidence. Source details and executable eligibility results remain in `HISTORICAL_SOURCE_AUDIT.v1.json` and `forecast-results.v2.json`.

No new training was warranted by these context facts. Baseline, Ridge and XGBoost are implemented; real approved-target fits/evaluations/selected models remain **0**. Synthetic machinery tests are not market evaluation. Forecast outputs remain unavailable. Session cost **USD0**, paid jobs **0**. The existing RunPod audit found no configured access; remaining credits and prior account usage are unknown. The reported USD25 account allowance is not verified remaining credit. A-002 requested no paid launch and capped it at USD0. No account request, paid retry or job was made during this refinement.

Only blocked/dependent work remains: A context integration/canonical joins, permitted Galaxy reuse, comparable forecast history and authenticated bounded paid execution if later needed. No research task is handed back to the user. Working-tree exclusions remain the original raw/derived inputs and ignored B acquisition/tool artifacts.

Push status: not pushed — awaiting explicit instruction. No deployment or production-data changes.
