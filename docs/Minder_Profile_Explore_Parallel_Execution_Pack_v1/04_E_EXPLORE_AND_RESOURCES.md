# E — Explore views and sourced resource delivery

Read context, actual ownership, file 07 contracts and file 08 evidence/privacy rules. Work in the assigned branch/worktree. Do not write migrations, D's state models, A's scoring, B's source acquisition or C's provider/grounder. Use their services through the agreed adapter boundaries.

## E1.1 — read interfaces and response composition

Inventory sufficient existing endpoints before adding routes. Implement separate product view/adapters only where needed. Publish schema-valid response examples early, including empty and unavailable cases, using actual public contracts and canonical IDs.

Use D's service interfaces for user state. During development, isolated schema-matching fixtures are permitted; they cannot become automatic runtime fallback on an error. Record which fixture must be replaced by which named dependency.

Preserve assessment/profile/evidence revisions so a view can show stale data accurately. Do not implement an alternate scorer, separate progress formula or second profile/task store. Commit E1.1.

## E1.2 — Profile/Explore/Overview read views

Compose the following from real supported services:

| View | Required result |
| --- | --- |
| Overview | Selected direction, next actual task, task progress, pending proposals and a small relevant evidence/resource selection |
| Career Match | A's recommendation/exploration results, input sufficiency, reasons, scope-qualified evidence and current ranking mode |
| Roadmap & Skills | Selected plan/stages, sourced requirements, user skill evidence, unknowns, supported gaps and tasks/resources |
| Tasks | D's tasks with plan/status/date filters, stable pagination and actual action capabilities |
| Progress | D's canonical counts/fraction, denominator explanation, activity history and separate skill-evidence information |
| News & Trends | E2.1 feed plus existing current/future market view, retaining unavailable forecast states |

Keep company-specific exploration separate from overall matching if already supported. No inferred company vacancy based only on a title.

Do not merge incomparable personal-only and market-supported scores into a new sort. Follow A's explicit grouping/order contract. Preserve current versus historical evidence dates and broad/narrow mappings. Omit internal market matrices from ordinary public views.

Test actual absent profile/no goal/empty plan/partial evidence/source failure and source-scope transformations. Commit E1.2 and hand working views to F before the whole feed is complete.

## E2.1 — bounded news and learning-resource feed

Build on existing B news/evidence and C resource retrieval functions, through separate E-owned product adapters. Do not recreate their provider clients or market-data pipelines. If retrieval is absent, use a small versioned reviewed public source list and bounded fetches; use genuine verified entries, not generated citations.

Pipeline:
1. Select supported role/skill/industry topics from the profile/selected direction. Do not send CV text, names or private chats to search providers.
2. Retrieve from approved public sources through existing access methods or approved bounded adapters.
3. Validate URLs, source identity, type and available dates; deduplicate by canonical URL/source identity without discarding meaningful distinct editions.
4. Retain permitted metadata/excerpts and real provenance. A valid link alone does not support a summary's factual claims.
5. Attach supported topic mappings and a short reason for relevance. Use deterministic metadata/excerpts where sufficient; any LLM-generated factual summary goes through C's existing grounding contract.
6. Serve stable, paginated results with source/date/type filters and availability states. Distinguish relevance ordering from market-demand ranking.

An achievable initial feed supports articles/news, videos and learning resources where those types have verified entries. Do not promise every topic has every format. A video listing without transcript supports its metadata, not invented claims about its contents. Unknown cost/duration/prerequisites/language remain unknown.

Support opening source details and D's save/unsave/dismiss/reset operations. Coordinate add-to-plan as an explicit D action. Existing source limitations and redistribution holds remain in force.

Implement bounded timeouts/retries and timestamped cached results where supported. A fetch failure may return a labelled last-successful result; it must not turn stale content into new news. No paid provider plan or unrestricted crawler is authorized.

Verify at least representative real permitted items for available formats, invalid/missing URLs, duplicate content, no-source results, stale cache and unsafe fetch inputs. Do not artificially increase evidence counts by duplicating articles. Commit E2.1 with source conditions and actual coverage.

## E2.2 — replace development fixtures and verify real composition

Use the agreed committed D/A/B/C revisions; inspect ancestry. Replace development adapters in normal runtime with actual service calls. A failed service returns a meaningful error/partial state, not fixture results.

Verify real profile changes affect relevance without altering market evidence; save/dismiss persists per user; selected direction/plan/task views agree; completed tasks update progress; source scopes survive API composition. Forecast-unavailable remains unavailable.

Provide concrete response examples for F and integration notes for A. Commit E2.2.

## E3.1 — handoff

Publish endpoint/schema versions, actual provider/source dependencies, coverage by content type, cache age behavior and remaining limitations. Identify any concrete C-grounder or D-state dependency with full SHAs. No unsupported national skill-demand or forecast claim.

Commit and normally push tested E checkpoints to E's assigned feature branch under file 10. Give A exact handoff SHAs; no pushes to other lanes or deployment.
