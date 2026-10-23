# E read/content checkpoint

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
