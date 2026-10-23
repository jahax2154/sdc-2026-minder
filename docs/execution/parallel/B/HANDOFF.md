# Session B market-service and RunPod handoff

Latest current-coverage handoff: [HANDOFF.v3.md](HANDOFF.v3.md), B3.2-R02, records coded MyCOL/DOSM expansion, precise six-digit scope, reconciliation with A and reuse limits. Earlier checkpoint text below remains historical.

Latest continuation: [HANDOFF.v2.md](HANDOFF.v2.md) records B3.2-R01, the complete accessible employer feed and actual historical-source investigation. The original B3.2 checkpoint report below is preserved as history.

Session B implemented the supported current-evidence service, bounded source/event collection, next-quarter forecasting machinery and checked artifact loader. Overall status is **limited**: neither family has enough comparable quarterly unique-ad history for a genuine forecast training/backtest. No model was selected. RunPod is blocked by missing credentials; account balance and previous jobs remain unknown. Session spending is **USD 0**, with zero paid jobs. Nothing was pushed or deployed.

This handoff is the B3.2 culminating local checkpoint. Its SHA is the commit containing this document; earlier exact checkpoints follow. The bootstrap ancestor `70dc99e96c51e2da3cacc0b84cdc729b2be33fd9` was verified before edits. No recovery/setup was repeated. Only B-owned paths changed.

| Phase | Status | Local checkpoint | Evidence |
| --- | --- | --- | --- |
| B1.1 | limited | `53d493e79c66f37b00f11b0608022761a725e86e` | Actual source acquisition, DOSM round trips, coverage; B1.1.json |
| B1.1-R01 | passed | `44e07abee156944194593e3c1fc0dca397ad7eab` | A-001 taxonomy edition/database metadata correction; counts unchanged |
| B1.2 | limited | `0b61ede1cb596cff6a0110d80c2a8769e385bd7e` | Callable current/forecast service, one real credible event; B1.2.json |
| B2.1 | limited | `bb408ece9b6c7b86de452536324bda1162f5f982` | All four forecast methods, dated splits, promotion contract; no real target fits |
| B2.1-R01 | passed | `514f0e23448f9e1e275f0cfb41e8908df252cc03` | Direct news-feature inputs also require approved provenance/coverage |
| B2.2 | blocked_external | `9dd5f5f615a840a47d5dfccc537995efd6873bdb` | Real eligibility runner returned unavailable_data; access/data blockers and zero-cost ledger |
| B3.1 | limited | `ba5d9a234cac334e7ba7b4a650b07e922fcaaccf` | Checksummed registry/loader, both families, no selected artifact |
| B3.2 | passed | commit containing this handoff | Publication of actual statuses, verification, costs and integration instructions |

Passing a software/refinement/handoff phase does not pass the missing training or data requirements. Historical reports remain history; no retrospective commits or generated approvals were invented.

## Actual evidence coverage

- DOSM: 952 verified source cells, 921 numeric and 31 missing, across 28 quarters from 2019 Q3 to 2026 Q2. Source-native occupation/industry marginal tables, not detailed-role/skill counts or joint tables. All cells are from the release available on 18 August 2026. Missing cells stay null; neither wages nor whole-labour-force measurements become advertisement targets. Latest broad observations are available through `broad_observations(as_of=...)` without allocation to canonical occupations.
- Bosch Malaysia: public official ATS lists 155 ads at collection. Forty details were inspected; 39 unique valid advertisements remain after one possible repost exclusion. This is a bounded active-ad snapshot, not a complete feed or quarterly advertisement inflow. Observation/collection date is **23 October 2026 MYT** (`2026-10-22T17:39:23.585614+00:00` is the precise stored UTC collection timestamp; use snapshot metadata as authority).
- Conservative role mappings cover four source-native O*NET codes: one software-developer advertisement, zero matching ads for the other three within this sample. Internship titles stay outside these occupation mappings. This does not show national absence or all developer opportunities. Source taxonomy is O*NET-SOC 2019; database release is 31.0.
- Literal positive qualification requests: Excel 5, SQL 4, C++ 2, Java 1, Python 1 advertisements. Skills overlap and must not be summed into total jobs. Preferred/negated mentions are excluded; title/dictionary coverage is partial. Technology source terms remain distinct from broad O*NET skill categories.
- One underlying MIDA semiconductor/talent announcement was retrieved, dated and hashed. It remains an ambiguous announcement, not verified hiring. No complete news-feed denominator or archived as-of news corpus was acquired; attention trends and empirical news ablation remain unavailable.

The committed factual snapshot includes IDs, dates, URLs, derived count inputs and hashes. Raw employer descriptions and source HTML stay in ignored lane artifacts; general redistribution rights are not asserted. The Bosch terms URL was unavailable; official careers linkage and public posting API documentation were retrieved. Source manifests preserve this distinction.

## A/C integration

Merge B's local commits through the final B3.2 checkpoint, preserving the focused refinements. Do not copy files or import source from another worktree. No shared-schema or dependency edit is required: the inherited foundation environment already contains the dependencies. A/C integration commits are outside B ownership. A's observed A-001/A-002 requests were read through Git refs, without modifying their directories.

```python
from minder_ml.intelligence.market_service import MarketEvidenceService

# A's integration_cli.role_aliases(catalogue) returns canonical ID -> native code.
market = MarketEvidenceService(aliases={"role": role_aliases(catalogue)})
current = market.current("role", "onet:15-1252.00", as_of=issue_timestamp)
future = market.forecast("role", "onet:15-1252.00", issued_at=issue_timestamp)
skill_current = market.current("skill", "source-term:sql", as_of=issue_timestamp)
skill_future = market.forecast("skill", "source-term:sql", issued_at=issue_timestamp)
facts = market.source_facts("role", "onet:15-1252.00")
```

Use a timezone-aware ISO timestamp. On 23 October 2026 the forecast target is **1 January–31 March 2027**, separately from observation dates. Every `current`/`forecast` result validates against `MarketResult`. Current count publication/availability is the derived snapshot release; original employer dates remain in `source_facts`. Supported zero within the sample differs from missing collection or unmapped identity. An earlier requested as-of time cannot reveal later observations.

A may inject this object into its `PersonalMatchingService(market, as_of=...)`. A's canonical IDs remain `onet:<code>`. A-001 explicitly accepts exact native identity aliases and rejects technology-to-broad-skill aliases; B complies. No taxonomy copy, title-based catalogue expansion or personal-fit change is introduced.

`service-examples.v1.json` contains actual current outputs, both unavailable forecast outputs and supporting ad facts. Keep current and forecast arrays separate. Ordinary UI/chat should consume the structured explanation, dated quantities and source URLs, excluding raw internal score matrices. `internal_index` remains null where no compatible share/YoY index exists. No new numeric current/future blend or recommendation score bypasses pending N01.

## Forecast implementation, runs and selection

Implemented methods are no-change, seasonal repetition, Ridge with train-only scaling/SVD, and bounded CPU XGBoost. Direct features use four contiguous observed quarters, known target calendar features and actual lead quarters; no future exogenous values or imputation. Issue origins use actual publication availability. Rolling/expanding fits enforce label availability with an embargo, tune only on validation, then report the untouched final temporal holdout. News/no-news ablations require matching eligible examples and approved archived document/coverage provenance.

`forecast-evaluation-contract.v1.json` freezes the promotion rule. Metrics are count MAE/RMSE/WAPE, with explicit zeros and coverage. No cross-series ranking is used, so ranking quality is not claimed. Descriptive validation residual ranges are not calibrated confidence intervals.

The actual committed-data runner was executed from B2.1 `bb408ec` against its immutable dataset checksum. Result: zero eligible series/examples, zero fits, zero empirical evaluations, zero selected models. See `forecast-results.v1.json`. Baseline predictions and Ridge/XGBoost fits/predictions were exercised only by clearly labelled synthetic software tests. Artifact loading was exercised with a temporary fictional baseline; no trained Ridge/XGBoost artifact reload is claimed. These outputs are not real observations or evaluation evidence. Broad DOSM history was not laundered into narrow-role targets or a publication-leaking retrospective accuracy claim.

The B1.1-R01 metadata correction updated the current snapshot digest without changing observed values. The immutable B2.1 eligibility dataset/report retains its original input lineage; the serving registry separately pins both current and forecast input files.

Default serving files are committed under `ml/data/market/`; they work after merging without untracked raw inputs. `serving-registry.v1.json` intentionally has `models=[]`. `ForecastRegistry` checks target/feature/promotion identity, dataset hash, source/series identity, package versions and artifact path/hash before trusted deserialization. It refuses unavailable-at-issue models and unevaluated lead quarters. No real model artifact is loaded tonight.

When real history supports promotion, export the immutable result/model manifest and checksummed artifacts into an A-accessible release artifact location, inject its local `artifact_root`, and publish a reviewed compatible registry. Never commit large weights or reference B's absolute directory. A trusted operator must control registry/artifacts; joblib is not a user-upload format. Model selection, artifact loading and application deployment remain distinct operations.

## Reproduction and refresh

```sh
source .env.local
PYTHONWARNINGS=error::RuntimeWarning PYTHONPATH=ml/src:ml/tests "$MINDER_PYTHON" -m unittest test_market_service test_forecasting test_service_contracts
"$MINDER_PYTHON" -m minder_ml.intelligence.market_training audit --output-dir ml/artifacts/session-b/new-audit
```

Final verification: **35 passed in 22.126 seconds**, including the actual 952 source-cell round trips. Earlier existing phase-two regression checks: **16 passed**. `B3.2-verification.json` records commands and the final log hash. `git diff --check` passed; all 13 bootstrap inputs still match hashes and read-only modes; all changed paths are B-owned.

The bounded collector can acquire another sample with `python -m minder_ml.intelligence.data_cli market-acquire --max-details 40 --output ml/artifacts/session-b/new-collection/snapshot.json`. It caps detail requests at 160, uses a 20-second HTTP timeout, no automatic retry and no paid service. Reuse acquired inputs; do not regenerate bootstrap hardlinks. Review a new immutable snapshot and publish updated compatible registry hashes before switching application evidence. The one-document event collector is `python -m minder_ml.intelligence.news`; its source plan is versioned. No background collection/scheduler deployment is claimed.

`market_training run` requires the exact dataset SHA and committed runner HEAD, writes local results/artifacts under the supplied lane output directory, caps fits/time and never launches paid resources. Do not run an empty-data request on RunPod to spend credits.

## RunPod handoff and remaining dependencies

`runpod_budget.json` is the single ledger. No configured key or private RunPod configuration was found; no authenticated account query, balance check or previous-job inspection was possible. **USD25 is the reported allowance, not verified remaining credit.** No top-up, duplicate job or retry occurred. Proposed operator limits are documented, not claimed as tested remote controls: one paid job at a time, maximum USD2/job, 900 seconds, zero automatic retries, subject to verified account rate/balance and an external stop mechanism before launch.

A-002 explicitly requests no paid job, cap USD0. A owns its separate local mathematical smoke. Its compatible personal-fit run remains dependent on N01 and real target/rubric availability. B acknowledged this in `requests/B-to-A-contracts.md`; no semantic target was changed and no paid A job was queued.

Dependent work remains:

1. Acquire comparable, dedup-verified historical quarterly MY role and skill advertisement counts, with source universe, taxonomy/method and actual publication vintages. A current snapshot cannot reconstruct that history.
2. Supply archived approved-source documents and complete feed coverage before empirical news ablation.
3. Privately configure RunPod credentials, verify balance/prior jobs and quote a bounded job with an actual external termination control before paid execution. Then process only immutable committed A/B manifests; return job ID, checksummed artifacts, stdout/failures and measured charges.
4. A/C integrate final service/refinement commits and retain unavailable output states. N01 remains pending for personal-fit arithmetic; it did not block this market engineering.

Excluded state is itemized in `B3.2-verification.json`: thirteen pinned raw/derived inputs preserved in the existing G0 shared snapshot; local raw acquisition/news responses; local run logs; non-secret `.env.local` reservations and caches. These remain local/uncommitted. Derived facts and verification summaries are committed; no new external backup was created. No credentials, real CV/profile data, models, database or unrelated files were staged.
