# Session B — Malaysia market evidence, forecasts and bounded RunPod execution

Work only in the G0-assigned B worktree. Read applicable instructions, handbook, canonical revision-5 context and ownership/contract manifest. Reuse existing market/source/model code; continue across all subgates without routine approval pauses.

Goal: real Malaysian current evidence and both next-quarter role and skill forecasting pipelines, backed by sources, chronological experiments and explicit unavailable states. Supply the stable service C/A need early. You are the sole operator of paid RunPod jobs for both ML lanes.

## Mandatory phase checkpoints

Read and enforce `07_PHASE_CHECKPOINT_RULES.md`. The table below defines commit boundaries; the detailed sections that follow define the work. Commit locally after each bounded phase, report the SHA, and continue eligible work. Link post-checkpoint repairs as `PHASE-ID-R01` etc. Defer human-dependent work explicitly; do not mark it passed. **Do not push until the user explicitly requests it.**

| Phase | Bounded output | Checkpoint requirement |
| --- | --- | --- |
| B1.1 | Acquire/normalise supported Malaysian observations | Working source pipeline and coverage checkpoint |
| B1.2 | Credible news signals and current-market service | Source-quality/current-evidence checkpoint; unavailable statuses work |
| B2.1 | Build next-quarter baseline/Ridge/boosting pipelines and historical splits | Runnable forecast pipeline checkpoint with target dates and no leakage |
| B2.2 | Run bounded training/backtests, including queued A jobs | Results/cost-ledger checkpoint; actual limits and failures visible |
| B3.1 | Load selected artifacts and expose both role/skill forecast outputs | Serving/provenance checkpoint; unsupported series explicitly unavailable |
| B3.2 | Publish market-service and RunPod handoff | Culminating B checkpoint with phase/refinement SHAs and resource status |

## Ownership and resources

Own market source acquisition, evidence/event processing, market mappings that reference A's canonical role IDs, current assessments, forecast training/inference, market tests/reports and remote-job ledger. Do not create competing occupation taxonomies, alter A's F formula, change C's routers/migrations, or edit root lockfiles. Submit dependency/contract requests to A.

Inspect actual RunPod balance/access and prior jobs. The reported budget is USD25 with no additional paid budget. Operate under this execution task's authorised bounded training scope; never silently top up. Record allocation/actual consumption across your jobs and A's requested jobs. Choose a job size after estimating cost; set duration/concurrency limits and stop idle/broken resources. Do not use all credits on the first tuning run. Groq serving is separate and does not inherently require RunPod.

## B1 — make the real evidence service usable

1. Audit acquired source tables/manifests and accessible history: entity scope, time frequency, available-at dates, country, units, actual field names and row coverage. No claim that Malaysia has no history merely because one feed is missing. Do not invent 2019–2025 data.
2. Implement actual bounded acquisition from accessible official/institutional/company/professional sources. Reuse acquired valid data first. Read licence/access terms where needed. A source URL in a manifest is not a functioning feed. If a source is inaccessible, record why and try a materially different appropriate available source; do not waste the night on repeated identical failures.
3. Prioritise the counts required by the prototype: unique valid observed role advertisements; unique advertisements requesting each skill. Preserve source universe, deduplication, window, taxonomy mappings, Malaysia relevance and availability. Skill counts can overlap. Do not represent advertised recruitment as all national employment.
4. Build the approved-source/event pipeline for credible news signals. Reject random personal posts/comments as forecast evidence. Separate announcements from verified adoption and hiring outcomes. Deduplicate syndicated stories; normalise attention changes for source coverage; preserve ambiguous/negative effects and global-versus-Malaysia scope.
5. Current market assessments use only supported compatible measurements and versioned transforms. News attention remains an auxiliary signal, not the ground-truth demand target. No internal scores leak into the ordinary user response; C receives structured internal values plus source-linked explanation facts.
6. Publish a callable current/forecast adapter early, with actual available data and meaningful statuses for missing series. This lets C integrate before the full training run finishes. Contract fixtures may exercise missing paths, but cannot masquerade as real current evidence.

## B2 — next-quarter forecasting and backtests

Initial target: the next full calendar quarter, with explicit start/end dates. On 22 October 2026 this means 1 January–31 March 2027. Distinguish forecast issue date, last available observation, target duration and actual lead time. Do not label a forecast after the last dataset row as 'next quarter from today' unless it is that actual target.

Implement baseline historical forecasts, Ridge and gradient boosting as compatible experiments using lagged/history/context features. Inspect reuse opportunities first. Forecast role counts and skill counts as separate output families; equal product priority does not force one model or equal numeric weights. Never fabricate targets or future exogenous features.

Use time-ordered rolling/expanding historical evaluations matched to the quarter target. Fit transforms/tuning on training/validation only; retain a final untouched temporal holdout. Respect publication delays and historical news availability. Compare with a no-change/seasonal baseline where supported and compare news-enabled versus no-news methods. Annual predictions from a frozen 2022 model are not the same experiment as quarterly retraining.

Report count errors, baseline comparisons, coverage and ranking quality when internal rankings are used. Handle zeros and sparse series honestly; disclose uncertainty and data limits. Never claim forecast accuracy from software tests or from a model trained to reproduce your own attention score.

Create actual RunPod jobs from committed runners/data manifests. You may execute A's immutable personal-ML job requests as well, returning job IDs, artifact checksum/location, stdout summary, failures and cost. You do not change A's target definitions. No parallel paid experiments unless the combined cap is explicit and within budget.

If a requested series lacks enough comparable history, return `unavailable` with precise reason and dates. Continue useful current evidence, other supported series and pipeline work. This product state is approved; do not call it a successful forecast run. A clearly labelled historical foreign-data research experiment may demonstrate mechanics, but never substitutes for a current Malaysian forecast or proves Malaysian accuracy. Do not launch paid unrelated research merely to spend credits.

The one-year/five-year ambitions stay documented, not added as untested extrapolations tonight.

## B3 — service, provenance and handoff

Save datasets/artifacts in the agreed per-lane locations, with source/model/schema/policy versions and checksums. Do not commit secrets, large raw corpora or environment-dependent paths. Supply retrieval/load instructions and an artifact that the integrated application can actually access without your worktree.

Meaningful checks: duplicate story/ad handling; source exclusions; geography and taxonomy mapping; missing collection vs zero; historical leakage; correct next-quarter target dates; unsupported forecasts stay unavailable; source dates match explanations; no preference update alters market evidence.

Return current and forecast coverage for BOTH role and skill families, actual experiment status, selected model/why, cost ledger, service examples, commit SHAs and exact integration dependencies. Company research in C may consume your source-quality/market interfaces; C owns employer-specific retrieval and presentation, not a duplicate global evidence pipeline.

Acceptance requires working sources/services and genuine experiment evidence where data supports it. Do not stop at an audit script or a list of potential websites.
