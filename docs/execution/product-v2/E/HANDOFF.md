# E read/content delivery — current E2 composition

Early published E1 checkpoint: `664b42423620eba26a8ffa125c20a747cef7ad75`.
Current E2 requires and includes D's committed handoff
`1cb81b1574e1ef263a47e3bb0e098c50482340c5` through a normal merge. Integrate the
cumulative E tip supplied with the final response; preserve both lanes' ancestry.
Do not cherry-pick only the E2 adapter diff without D.

Current implementation uses D `state_view(store, authenticated_owner)` for a
consistent profile/direction/plans/active_plan/progress/resource_states snapshot.
Canonical progress passes through unchanged; task filtering never redefines it.
No new SQL, migrations, state store, provider calls or source acquisition in E.

**E2 response refinements for A/F:** roadmap/overview `data.direction` is D's raw
nullable Direction record, and `data.active_plan` is the raw nullable PlanProgress.
This replaces the E1 temporary D-operation wrapper. Progress is available with
status empty and fraction null when no active plan/eligible tasks exist.
Overview now includes active-plan tasks, canonical progress, pending proposals,
up to three real resources and next_task. Next task means an unlocked ready task
in the selected plan, by actual scheduled instant then stored task_ids order;
unscheduled tasks follow scheduled tasks. It never selects an alternative goal or
schedules anything. Null means none is ready/selected. Task rows include supported
operation names; D still validates version/dependencies/feasibility on each write.
Roadmap exposes known requirements and skill evidence; `gap_assessment_status`
explicitly says no new gap computation (use A's selected-role assessment).
Progress exposes persisted progress_event_ids and separate skill evidence, with
no fabricated detailed event timeline or skill certification.

Resource records now include nullable `interaction` from D. List requests support
`saved:boolean` and `dismissed:boolean`. Default dismissed=false excludes dismissed
items; use dismissed=true to inspect them; reset through D makes them visible again.
Use D's current expected_version and idempotency controls for saves/dismiss/reset.
Both current resource IDs are already accepted by D's existing resolver; no new
resource resolver or public catalog schema is needed for this small coverage.

## Current validation and remaining limits

Nine focused E tests passed. Real 1016-role source runtime and fictional-user WSGI
journey passed: A recommendation equality, source statements, unavailable forecast,
selected plan/next task, resource addition, canonical progress after completion,
filtered-task progress consistency, saved-resource filtering, roadmap version
agreement and no mastery inference. Zero provider calls and external fetches.
The journey uses a disposable E-only database and leaves no listener running.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests "$MINDER_PYTHON" -m unittest test_product_views test_product_content
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/E/check_journey.py
```

`RESPONSE_EXAMPLES.json` contains observed fictional-user responses from that
journey, with ProductView schema validation; it includes no bearer token. Regenerate
with the journey's `--examples` flag. Examples use actual sources, no mock service.

Combined backend discovery at the first E2 run:64 tests,63 passed, one obsolete
D test expectation errored: test_product_state.py test_wsgi_contract_status_and_
unavailable_states expects `/api/product/views/news` to be unavailable. It is now
implemented and returns ProductView. D/A must update that owner-controlled assertion
when integrating E; E did not edit D's test. A's older all-unavailable bootstrap
checks likewise describe P0.2 and are superseded for implemented capabilities.
Later E tests add three further passing focused checks; a full-suite pass is not
claimed. News/articles/videos, automatically mapped occupational learning gaps,
automatic schedule generation and detailed D activity event read API remain absent.
Two verified metadata entries are intentionally the complete initial feed.

## E1 checkpoint record (historical first useful slice)

Launch dependency: `fbddeb8` (P0.3), including A/B/C contracts and sources listed in
the launch record. Owned adapter modules register through A's existing discovery;
no central router, contract, provider, state writer, scorer or migration changes.

## Implemented reads

GET/POST `/api/product/views/{career-match,roadmap,tasks,progress,overview,news}`
returns the shared ProductView envelope plus `read_version: product-reads-v1`.
POST uses an object; GET has the same default empty request. No query-string
parsing was added. Bearer authentication and owner resolution remain in Application.

`career-match.data` is A's actual public career-context unchanged. Preserve its
ranking groups, questions, profile/policy/evidence versions, statements and source
scopes. `selected_role_ids` / `selected_skill_ids` retain A's at-most-three limits.
No saved profile yields unavailable/profile_required; disconnected personal service
yields recommendation null. No development fixture fallback exists.

`roadmap.data` contains real owner-scoped plans, direction, profile skill evidence,
known catalogue requirements and explicit unknowns. `tasks.data` wraps actual tasks
with plan_id/state_version, total/offset/next_offset, plan_versions and D progress.
Filters: plan_id, state, scheduled_from/to; stable order plan_id,task_id; limit1..50.
This pagination is a fresh read, not a frozen multi-page snapshot; compare versions
after writes. A foreign plan_id fails404 rather than returning another user's plan.

`progress.data` delegates D's advertised GET progress operation. Until D is
integrated this view is unavailable. Overview is partial with actual tasks and
pending proposals; next_task remains null pending selected-plan/order integration.
News is partial: learning metadata plus A market statements; no news feed claimed.

## Small sourced resources

POST `/api/product/resources` accepts topic_ids, types, publishers,
published_from/to (ISO dates), offset and limit1..50. POST
`/api/product/resource-detail` accepts only `{resource_id}`.

Response version `product-content-v1`. Resources retain C's stable IDs
`python-tutorial` / `microsoft-tsql` and original Source records. Coverage: two
learning resources, zero articles, zero videos. No new acquisition was needed.
The Python Software Foundation and Microsoft Learn metadata was already retrieved
and source-hashed in C's `official-learning-options-v1` library. Reuse only those
existing metadata descriptions; no new summary claims or LLM calls.

Unknown publication date, language, effort, total cost remain null. Source
available_at is shown as original retrieved_at, never refreshed to request time.
Cache mode is versioned_verified_metadata, revalidated_on_request=false; current
availability is unverified. Dated filters exclude undated items. Empty/unsupported
topics or formats yield an explicit empty result. Deduplicate canonical URLs;
approved HTTPS hosts only. Requests cannot supply a fetch URL.

Ordering is exact topic match then stable resource_id, never market demand.
Explicit topic filters or exactly matching profile evidence subject IDs affect
relevance; free text and private documents are never sent externally. No inferred
role requirement or mastered skill. D resource-state is returned separately and
stays unavailable until its committed implementation is integrated. Save/dismiss/
add-to-plan controls must use D's writes, never this adapter or client-only success.

## Checks and consumer action

Six focused tests pass with the existing Python environment:

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests "$MINDER_PYTHON" -m unittest test_product_views test_product_content
```

Checks cover shared envelope validation, absent profile/disconnected service,
empty plans, owner-isolated tasks, actual plan reads, capability discovery,
pagination/filtering, unknown dates, source IDs/details, unsafe URL rejection,
duplicate URLs and source failure without fixture fallback. These checks are
engineering evidence, not product approval or forecast accuracy.

A: integrate the full E checkpoint SHA supplied with this handoff, then expose the
already-discovered routes. F: use these JSON shapes and preserve null/unavailable
states. D remains a separately committed dependency; do not import active files.
Initial local untracked raw/derived input directories are excluded, not backed up
by E's commits. No private config, database, upload or generated artifacts committed.
