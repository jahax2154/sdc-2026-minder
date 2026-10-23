# P0.2 — product bootstrap contract v1

Additive private document interface: [DOCUMENTS_CONTRACT.md](DOCUMENTS_CONTRACT.md),
policy private-documents-v1. Registration is published; storage/extraction remains
unavailable until D's committed module advertises its implemented operations.

Existing working routes and schemas are authority. Reuse
../product/llm/FRONTEND_CONTRACT.md, its envelope schema/examples, and
contracts/parallel-services.v1.schema.json with service_contracts.validate.
No OpenAPI/FastAPI conversion, second user/task store, scorer or provider client.

Transport: synchronous JSON, same-origin /api, private bearer owner resolved by
Application before product dispatch. Current error envelope {code,request_id}
and401/404/409/413/415/422/500 apply. No CORS/cookie/streaming/transcript API invented.
Versioned writes fail409; success means persisted state. Idempotency must bind
exact body/scope, not only a UI click. Explicit edits use existing direct authority;
proactive changes remain exact previews through existing ActionExecutor.

## Working first slice

| Method/path | Request/response | Owner |
| --- | --- | --- |
| POST /api/session | Empty object -> private token/profile_id; no profile yet | Existing C |
| GET/PUT /api/profile | Profile; PUT {profile,expected_version:null|string} -> current Profile | D state; existing handler |
| POST /api/intake | Existing TXT draft<=64KiB, no automatic mastery/save | D state |
| GET/POST /api/career-context | Existing public context, focused questions, scoped ranking groups | Existing A, E projection |
| POST /api/roles,/api/role-requirements,/api/role-evidence | Existing canonical role/detail/source/trace contracts | Existing A |
| POST /api/chat | Existing C request and ChatResponse; Qwen current profile | Existing C |
| GET /api/agents,/api/proposals,/api/action-history | Actual events/proposals/history | Existing C |
| POST /api/direct-action,/api/proposal-decision,/api/undo | Existing scoped requests/preview/hash/version/idempotency | Existing C |
| GET/POST /api/plans,/api/pathway-preview,/api/learning-resources | Existing schemas/source library | D plans, existing C resources |
| GET /api/product/capabilities | {contract_version,operations:[{method,path,owner,status,module}]} | A, implemented |

Two compatible optional metadata extensions are published now:
Profile.career_context {display_name<=120,education/experience/goals<=4000 strings},
all explicitly self-reported, not skill evidence or direction selection.
Task may retain title<=200, description<=4000, resource_id nullable, skill_ids<=20.
D validates canonical references and current state; unknown duration/cost remains
null. No existing required field, state enum or completion/mastery rule changes.

## Additive operations — fixed paths, not claimed implemented

A product_routes.py registers the operations below. Missing modules/operations
return404 product_capability_unavailable, never fixture fallback. D/E publish a
module OPERATIONS set of implemented (method,full_path) tuples and
dispatch(app,owner,method,path,body). Registry then advertises only those tuples.
A alone edits central routing; new routes require a focused contract handoff.

| Method/path | Owner/module | Bound input / output meaning |
| --- | --- | --- |
| GET/PUT /api/product/direction | D product_state | DirectionWrite for PUT; chosen role/nullable active plan/version; preserve prior plans |
| POST /api/product/tasks | D product_state | TaskCreate; same plan/state service, no mastery certification |
| POST /api/product/task-action | D product_state | TaskAction; only actually supported operations, stale writes fail |
| GET /api/product/progress | D product_state | Canonical selected-plan completed/eligible counts, nullable fraction and denominator explanation |
| GET/PUT /api/product/resource-state | D product_state | ResourceStateWrite for PUT; per-owner saved/dismissed flags, retry-safe |
| POST /api/product/resource-to-plan | D product_state | Explicit resource/plan/version/idempotency; preserve unknown metadata |
| POST /api/product/intake-correction | D product_state | Owned draft/current profile version and reviewed changes; never inferred competence |
| GET/POST /api/product/views/overview | E product_views | ProductView envelope |
| GET/POST /api/product/views/career-match | E product_views | Same A groups/reasons/source scopes, hide ordinary score matrices |
| GET/POST /api/product/views/roadmap | E product_views | Existing plan/requirements/evidence/unknowns |
| GET/POST /api/product/views/tasks | E product_views | D state projection, filters do not redefine canonical progress |
| GET/POST /api/product/views/progress | E product_views | D's canonical calculation, no second formula |
| GET/POST /api/product/views/news | E product_views | Source/resource/feed projection, unavailable forecast retained |
| POST /api/product/resources,/api/product/resource-detail | E product_content | Bounded real source library/feed/detail, stable IDs |

contracts.schema.json defines strict first-slice input schemas and ProductView.
TaskCreate references the existing canonical Task schema by urn, not a duplicate.
Examples.json labels requests as planned and captures actual bootstrap
capability/auth/unavailable results. D/E refine their operation-specific response
schemas/examples in owned *_schemas.py modules; A reviews/publishes compatible
shared revisions before F relies on new fields. Do not freeze every implementation
detail or fake completion from a proposed schema.

D migration interface: product_migrations.migrate(store), sole new writer.
Runtime initializes existing migrations1-4 without a provider call; new chain starts5.
D tests fresh DB and disposable upgrade, never another lane's running DB.
D should expose a Python state view helper for E through product_state (same Store),
with exact signature recorded in D's first committed handoff. Until then E can
compose existing /profile and /plans services; no new SQL or independent user DB.

Every response keeps current profile/state/evidence/policy versions, actual nullable
dates and publisher scope. News relevance is not demand ranking. Sector context,
related shortage groups and category offering proxies cannot become narrow-role
national counts. Ordinary frontend/LLM output hides internal matrices. No synthetic
lab rows in normal views. A task/resource action is not assessed mastery.

Current optional context metadata does not enter A's skill rubric; a partial profile
still saves and produces focused questions. Availability never silently reschedules
a plan. An unavailable capability remains in CAPABILITIES.md, not silently dropped.
