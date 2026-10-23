# Session B — expanded current evidence and historical-source investigation

Current Malaysian source evidence is usable after merging the B continuation commits. B owned the source research and implementation throughout; no dataset research is assigned to the user or A. Historical forecast training remains **deferred** because the acquired sources do not establish the approved comparable quarterly unique-ad targets. There is no trained forecast, empirical accuracy claim or model selection.

| Refinement | Actual result | Checkpoint |
| --- | --- | --- |
| B1.1-R02 | All 155 accessible native employer requisitions inspected; current handoff delivered early; limited market breadth | `b8478a32ec57b31bcc5928d72c93a61b750eb951` |
| B1.1-R03 | Actual records/access inspected across 33 endpoint attempts; real corpus and official count extraction; limited forecast eligibility | `ee4096cffd2811dc3d1e56273dacd05cbc1c6e4a` |
| B1.2-R01 | Callable official source-label facts and employer evidence remain separate; serving refinement passed | `653bb6775e70df75edcbe79412e14911fcf1bfa0` |
| B2.1-R02 | Updated eligibility audit accounts for all acquired source families; refinement passed | `db06fedf593d3e448d1e2c9a3d77b52703bb0e06` |
| B2.2-R01 | Actual immutable real-data runner returned unavailable_data; training deferred; USD0 spent | `ff4036eaef04a9164afb936784ba682c69d018be` |
| B3.2-R01 | Final verification and A handoff published | commit containing this handoff |

The earlier HANDOFF.md and phase reports retain their historical evidence. The continuation above supersedes their initial 39-ad sample coverage. Nothing was pushed, deployed or written to production data.

## Current evidence and A integration

The original 40-inspected/155-listed limit was a collector-selected cap, not a source/API restriction. The expansion inspected all 155 listed native requisitions: 40 hash-pinned details were reused after checking current listing membership/release dates, and 115 further details were fetched without failures. The new default cap is 160; completeness flags remain explicit if a future feed exceeds that cap.

All 155 native requisitions are distinct. Five same-template/different-requisition cases are retained and flagged, since identical text is insufficient proof of a repost. Repeated native requisition IDs are deduplicated. One ad lacks a qualification section: role denominator is 155, skill denominator is 154. Missing qualification evidence is unknown rather than zero requested skills.

Actual source-scoped current counts are **5 Software Developer title matches**, **27 Excel**, **11 SQL**, **8 C++**, **6 Python** and **4 Java** requesting ads under the versioned qualification rule. Skills overlap. Four conservative native occupation mappings are supported; unsupported canonical roles retain unavailable states. Release dates span 2020–2026, with 32 records predating 2026. Dates and old-release/template/missingness flags are visible in source facts. Listed feed membership is not proof of current hiring, new posting volume or filled positions.

The packaged snapshot/registry need no untracked raw files or sibling-worktree paths:

```python
from datetime import datetime, timezone
from minder_ml.intelligence.market_service import MarketEvidenceService

issued_at = datetime.now(timezone.utc).isoformat()
market = MarketEvidenceService(aliases={"role": role_aliases(catalogue)})
role_current = market.current("role", "onet:15-1252.00", as_of=issued_at)
skill_current = market.current("skill", "source-term:sql", as_of=issued_at)
role_forecast = market.forecast("role", "onet:15-1252.00", issued_at=issued_at)
facts = market.source_facts("role", "onet:15-1252.00")
```

A owns `role_aliases(catalogue)` and canonical IDs. Technology terms remain distinct from broad skill categories. Use an actual current timestamp: a frozen `2026-10-23T00:00:00Z` predates this expansion's availability and correctly returns unavailable evidence. No shared schema/root dependency or A/C file edit is required by B. `requests/CURRENT_MARKET_HANDOFF.v2.md` was the early handoff; v3 adds source-native official observations. `service-examples.v2.json` and v3 record actual validated calls.

Official source-label evidence is also callable:

```python
source_label = "dosm:jmi:published-role-label:software-developers"
official_current = market.current("role", source_label, as_of=issued_at)
official_facts = market.source_facts("role", source_label)
official_history = market.published_role_observations(as_of=issued_at)
```

The latest explicit fact is **19,899 published online job offerings for Software Developers, 2026 Q2**, published **18 August 2026**; the other numeric point is 20,089 for 2026 Q1. There are 35 numeric observations across seven source labels and 42 missing label/quarter cells. Source quantity/unit/universe, original publication date, retrieved byte availability, URL, hash and classification limitations are retained. These published offerings are not added to the five employer requisitions or silently treated as deduplicated unique ads. A source label is not a new canonical occupation catalogue or an automatic MASCO/O*NET crosswalk.

## Historical targets: actual records and exact gaps

`HISTORICAL_SOURCE_AUDIT.v1.json` records URL, geography, measurement, dates, role/skill classification, actual fields/records, access, missingness and limitations for every bounded endpoint attempt. The accompanying Markdown explains why each source does or does not support each target. This is not a list of potential websites.

- **Existing DOSM history:** 952 verified cells, 921 numeric and 31 missing, 28 quarters from 2019 Q3 to 2026 Q2. The 2026 Q2 attachment contains separate economic-activity and occupation-major-group tables. Its old cells are an August 2026 release vintage. The separately retrieved Q1 attachment supplies an earlier June 2026 broad-data vintage. Neither attachment contains detailed-role IDs, ad-to-skill records or skill-request counts. Broad sector/major-group totals cannot be allocated to narrow roles or technologies.
- **Explicit DOSM occupation releases:** eleven actual pages yielded 35 numeric role-label counts, including seven consecutive quarters for four labels and only two numeric Software Developer observations. Top-list omission or a ranked name without a count is missing, not zero. Unique-ad deduplication, positions-per-ad equivalence, classification edition for every release and independently archived historical bytes remain unverified. They are useful dated source facts, not a long verified target series.
- **Original JobStreet records:** 69,024 distinct real IDs with full descriptions, parsed listing dates from 23 March 2023 to 8 May 2025, and eight populated quarters. There are no acquired rows for 2024 Q3–Q4. The uploader describes a current weekly scrape, not complete historical collection windows including expired ads. Historic per-record availability is absent. There are 647 literal location values but no ISO country field; 2,252 role strings and 37,430 salaries are missing. The cleaned research mirror has the same IDs/date distribution and no descriptions; it is not an independent population or requested-skill source.
- **Other actual access checks:** correct PERKESO LMX entry/statistics/dashboard/publication pages were retrieved but yielded no acquired machine-readable quarterly role/skill target series. TalentCorp MyNSR describes a skill framework rather than observed ad frequencies. Old MyJobProfile and DOSM-linked ILMIA alternatives failed executable certificate validation; the documented HTTP alternative returned 502 and one archived attachment returned 404. No TLS validation or access control was bypassed. All responses/errors are recorded, and materially different accessible sources continued.

The original JobStreet ZIP was acquired only after file metadata diagnosed the initial 30MB download cap: one explicit 80MB compressed/250MB unpacked bound allowed the actual 52,725,731-byte archive containing a 166,519,093-byte CSV. Original dataset metadata labels it Apache 2.0; raw advertisement redistribution rights were not independently certified. Raw descriptions stay local.

Executable `data_cli market-corpus-audit` processed all original records into `ml/data/market/research/jobstreet-corpus-counts.v1.json`. It contains real dated frozen-corpus counts, role-title matches, literal technology mentions and a separate conservative explicit-request-clause subset. Missing quarters remain absent. This is **descriptive research**, not an approved complete-quarter target, historical model experiment or present-day Malaysian forecast. `market-published-roles` separately reproduces the 35 official observations from pinned document bytes. Probe/replay/audit/extraction commands and finite source plans are committed.

What remains missing is precise: sufficiently long comparable quarter-level counts of distinct valid role ads and ads requesting each skill; complete collection/exposure windows including closed/expired ads; supported classification and geography; and actual input/outcome publication vintages. A surviving current corpus or catalogue of skills cannot reconstruct those missing observations.

## Experiments, verification, resources and remaining work

No-change, seasonal, Ridge and XGBoost are implemented with publication-aware temporal controls, train-only transforms, validation tuning and untouched holdout handling. The updated committed runner was actually executed at `db06fed` against its immutable dataset SHA. It audited every newly acquired source family and returned **unavailable_data: 0 eligible examples, 0 fits, 0 empirical evaluations, 0 selected models**. See `forecast-results.v2.json`. No different-target research model was trained; the frozen-corpus compilation is labelled separately. Synthetic unit fits are software evidence only.

Both role and skill forecasts remain unavailable for the next full calendar quarter, **1 January–31 March 2027** for an October 2026 issue. Source publication delays and last observations remain distinct from the forecast target. Current evidence continues to work independently; no new personal-fit arithmetic, current/future blend or internal-score UI is introduced by B.

Final focused verification: **43 tests passed in 22.504 seconds**, including actual DOSM cell round trips, missing-vs-zero, deduplication, provenance/date guards, source-unit separation, target eligibility and artifact checks. `B3.2-R01.json` records the command/log hash and actual checkpoint SHAs. All 13 original raw/derived inputs still match hashes and read-only modes. All changed paths are B-owned. Earlier phase/refinement test runs remain recorded separately.

`runpod_budget.json` remains the single paid ledger. Latest recheck found no configured key/private config; authenticated balance and previous account jobs remain unknown. **Session spend USD0, paid jobs 0.** USD25 remains the reported allowance, not verified remaining credit. A-002 still explicitly requests no paid launch and has a USD0 cap. No empty-data job was launched. Any future paid execution still requires actual account/balance/rate/stop controls and an immutable runnable request; no new budget, retry allowance or top-up is inferred.

Remaining work is the specific historical collection/vintage dependency above and A/C integration of these committed owner changes. B retains source-investigation/adapter ownership. No account/spend/scope question is required for the usable current delivery; no dataset-research task is transferred to the user. Personal numerical policy and any canonical crosswalk acceptance remain A-owned.

Raw artifacts remain ignored/local: investigation 25 files / 77,265,983 bytes; acquisition 162 files / 2,358,217 bytes; expansion intermediates/log 4 files / 2,805,672 bytes. Compact factual outputs, provenance hashes, audit results and handoffs are committed. No external raw backup was created, no credentials/real CVs/databases/models were staged, and the original read-only source snapshot was preserved.
