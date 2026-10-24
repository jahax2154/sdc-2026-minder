# Data meanings and API contract binding

This defines required semantics, not fictitious existing endpoints or a mandate to recreate these as new tables. A/D/E bind each concept and operation to current code at P0.2. Reuse actual enums, IDs, validation and migration conventions. If the backend does not expose OpenAPI, use appropriate machine-readable schemas and tested examples rather than changing framework merely to obtain OpenAPI.

## 1. Logical records and relationships

| Concept | Minimum meaning to preserve | Relationship and constraints |
| --- | --- | --- |
| User/session | Server-resolved identity and actual auth/demo-session boundary | All private reads/writes are scoped; arbitrary client IDs do not authorize access |
| Profile | Education, experience, goals, interests/preferences, constraints, availability, revision and update time | One canonical user profile, with existing history semantics |
| Skill evidence | Canonical skill reference, provenance, self-report/assessment status, scale/value when supported, date | Missing value is unknown; no title-based proficiency inference |
| Intake document | Owner, storage reference, accepted type/size, processing status, extraction provenance | Private; extracted candidates are correctable; not public evidence |
| Preference | Target type/ID, explicit state, source and revision | Missing/neutral/dislike differ; preserve active reset/idempotence rules |
| Assessment | Profile revision, policy/model revision, evidence revision, sufficiency, reasons, mode | Numerical internals remain server-side; stale inputs identifiable |
| Selected direction | User's selected canonical role/goal and active plan reference | Explore recommendations do not automatically change this |
| Plan/roadmap | Owner, direction, version, state, stages and provenance | Retain historical plans; use same agent/manual services |
| Requirement/gap view | Supported role requirement, source, user evidence and assessment availability | Unknown competence is not a proven gap; mappings record broad/narrow scope |
| Task | Owner/plan, title, actual status, order/dependencies, optional skill/resource, schedule, version | Optional due dates/duration not fabricated; use valid transitions |
| Task event | Operation, task/version, time, actor/source and retry identity where supported | Complete/undo/reschedule audit and progress use persisted events |
| Progress view | Plan, counts, denominator definition, fraction if denominator exists, observation time | No double-counted parent/child tasks; not career readiness |
| Source/evidence | Stable source/claim ID, publisher, URL, passage/derivation, dates, geography, measurement and mapping scope | Existing A/B/C evidence contracts remain authority |
| Content/resource | Stable content ID, type, title, source/URL, available dates, supported topics, permitted excerpt/summary, known prerequisites/cost/duration | Shared public metadata separate from private per-user interactions |
| Content interaction | Owner/content ID, saved/dismissed state and update version/time | Idempotent; never implies learning completion |
| Proposal/action | Exact intended changes, target versions, authority/state and persisted execution result | C's approval boundary preserved; no client-only execution |

Use database constraints/transactions appropriate to existing implementation. Do not introduce event sourcing, a new queue or microservices solely because events are mentioned here.

## 2. Operation inventory to bind to actual HTTP paths

The labels below are logical operations, not route names. Existing working routes take precedence. New routes follow current conventions and receive explicit owners.

| Family | Operations to support or explicitly report unavailable | Primary owner |
| --- | --- | --- |
| Profile | Read/save/edit; skill/evidence/preferences; availability; supported document intake/status/correction | D; A coordinates assessment boundary |
| Recommendations | Assess/read current result; explore/detail role; feedback/reset | Existing A service; E composes public view |
| Direction/plan | Select direction, get plan/history/requirements, supported explicit plan changes | D with existing C services |
| Tasks | List/detail/create/edit/schedule/complete/undo; supported cancellation | D writes; E views |
| Progress | Current plan progress and activity/history | D computation; E composition |
| News/resources | List/filter/detail/source; saved/dismissed views | E content reads; D user-state writes |
| Resource use | Save/unsave/dismiss/reset; add selected resource to plan | D through shared service |
| Current/future market | Existing typed observations and forecast availability | B/A evidence; E presentation |
| Minder/Mindbots | Existing chat, events, proposals, approve/reject, action/job result and available controls | C contract; F UI |

A/E/F must not enable a UI control whose operation is unimplemented without an honest disabled/unavailable state. Required but unavailable operations remain in the gap ledger; they are not silently removed from scope.

## 3. For each actual operation, publish

1. Actual method/path, implemented or planned status, owner and backing service.
2. Request/response types, required and optional fields, enums, canonical IDs and nullable/missing meaning.
3. Auth/session and ownership behavior; cookie/token, CSRF/CORS and origin/proxy requirements as actually implemented.
4. Version/If-Match or existing conflict mechanism; retry/idempotency behavior for writes.
5. Persistence success boundary and resulting invalidated/refetched views.
6. Normal, empty, invalid, stale, forbidden, unavailable and retryable-failure examples.
7. Evidence/policy/profile revisions and what public presentation may expose.
8. Pagination/filter/sort stability where needed; timestamps and date-only semantics.
9. Backend SHA and validation command for examples. Label fixtures explicitly and keep them separate from observed data.

Do not add a second error envelope purely for this pack. Bind the semantics to current conventions. Sanitized errors must not leak secrets, internal paths, prompts or other users' data.

## 4. Changes and invalidation

| Operation | Refresh/invalidate | Must not happen implicitly |
| --- | --- | --- |
| Save skills/interests/preferences | Profile; dependent recommendation revision; resource relevance as appropriate | Automatic new selected role or plan rewrite |
| Change availability | Profile; feasibility view; concrete agent proposal if appropriate | Unapproved rescheduling of existing tasks |
| Select direction explicitly | Selected plan, roadmap/requirements and related views | Erasing old progress/history |
| Complete/undo a task | Task, canonical progress, recent activity and relevant agent context | Assessed skill mastery or fabricated completed learning |
| Save/dismiss an article | That user's resource state/feed | Changing market evidence or completing a task |
| Approve a proposal | Exact approved targets and dependent views | Arbitrary later changes or repeated execution |
| Receive new source evidence | Dated market/feed views and authorized assessment refresh | Silent goal switch or synthesized future certainty |

Re-fetch through existing shared cache/client conventions. No new global event bus is required if existing query invalidation/refetch suffices.

## 5. Concrete acceptance examples

These are behavior examples, not made-up API responses:
- Partial profile saves; assessment returns focused missing questions, not a fabricated score.
- A self-reported Python entry remains self-reported after a task is completed.
- A latest employer observation preserves its employer/source universe when shown in Career Match.
- A sector-level series retains its own date/unit; it is not recast as a narrow-role count.
- A saved article appears after refresh for the same user and is inaccessible through another user's interaction record.
- A stale task edit fails safely and offers refresh; it does not silently overwrite an approved agent change.
- A rejected rescheduling proposal leaves tasks unchanged; repeated approval does not apply twice.
- No eligible forecast produces an explicit unavailable response, not a numeric zero or decorative projection.

## 6. Contract changes during parallel work

Make small additive changes where possible. The owner posts a committed change request with reason, affected consumers and examples; A accepts/publishes the shared revision. Consumers integrate that named revision, not an uncommitted sibling worktree. Breaking changes require coordinated adoption and compatibility handling. Avoid renaming stable IDs or paths for cosmetic consistency.
