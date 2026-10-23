# C → F actual frontend contract — CL1

Checked backend base: `8c77d69` (full SHA in examples.json). This is an implementation export, not a proposed API. CL1 chat still supports Bosch derivations only; CL2 will add A's EvidencePassage v1. F can wire all operations below now and render returned statements without synthesising facts.

## Transport and lifecycle

C acceptance entry is `apps/frontend-web/index.html`, `app.js`, `style.css`, served by `minder_app.dev` at http://127.0.0.1:9103/. Routes are hash views #overview, #profile, #minder, #mindbots, #explore. JavaScript uses relative `/api/`; the same Application also listens on 127.0.0.1:8103. This is the acceptance/prototype frontend, not the standalone HTML/Replit product. F owns that connection: use a configured same-origin server proxy to the named backend; never ship a remote browser pointing to its own localhost. No CORS headers are implemented. Browser cookies are unused; thus no cookie-based CSRF token. All private endpoints require `Authorization: Bearer <session token>`. Treat the token as a credential, keep it out of logs/fixtures/URLs. Owner is resolved exclusively from the token, never a request owner ID.

All operations are synchronous JSON objects, HTTP 200 on success. No SSE, streaming, conversation ID, conversation CRUD, persisted message transcript/history, job polling endpoint or proposal-detail endpoint exists. Refresh proposals through the list and select by preview.proposal_id. Chat persists a private grounding ledger, not a conversation. F must label local display history as transient and must not claim server conversation persistence. A scheduled worker must actually run for agent notices; `deployment_scheduler_verified:false` does not certify continuous operation.

## Actual operation inventory

Schemas named below are `$defs` in `contracts/parallel-services.v1.schema.json`, with the executable semantic checks in `service_contracts.validate`. Wrappers are listed explicitly. Unknown/optional values retain backend nulls; unknown never means zero. IDs are opaque canonical identifiers; do not join on job titles.

| Method/path | JSON request | Successful response / constraints |
|---|---|---|
| GET /api/health | none, public | `{status:"ok",integration_mode:string}` |
| POST /api/session | `{}`, public | `{token:string,profile_id:string}`; creates owner, does not create profile |
| GET /api/profile | none | Profile; 404 until saved |
| PUT /api/profile | `{profile:Profile,expected_version:string|null}` | Profile with server-owned profile_id/group/version; null only for initial save |
| POST /api/intake | `{text:string,channel:"chat"|"cv",filename?:string,content_type?:"text/plain"}` | staged draft, no profile mutation; TXT only, 64KiB limit |
| GET or POST /api/career-context | POST `{selected_role_ids?:string[],selected_skill_ids?:string[]}` | public context incl recommendation, market, sources, limitations; select at most 3 of each; internal arithmetic is not UI material |
| GET /api/assessment-reference | none | actual personal service reference (404 if unavailable) |
| POST /api/roles | `{query?:string,offset?:integer,limit?:integer}` | `{total,offset,catalogue_order_not_rank:true,roles:[{role_id,label,eligibility,missing_reasons}],applied_query,can_clear_filter:true}`; limit clamped 1..50 |
| POST /api/role-requirements | `{role_id:string}` | `{role:Role,limitation:string}` |
| POST /api/role-evidence | `{role_id:string,trace_id?:string,expected_profile_version?:string,view_role_ids?:string[]}` | `{policy_version,records:MarketEvidence[],passages:EvidencePassage[],limitation,trace?:RecommendationTrace public projection}`; trace requires current matching profile/version/view; 409 stale |
| GET /api/source-market-catalogue | none | `{records:object[],limitation:string}`; source-native catalogue, not canonical occupations or leaderboard |
| POST /api/source-market-context | `{occupation_system?:string,occupation_version?:string,occupation_code?:string,evidence_ids?:string[]}` | source service context; preserve source-native record scope and limitations |
| POST /api/chat | `{message:string,expected_profile_version:string,selected_role_ids?:string[],selected_skill_ids?:string[]}` | ChatResponse in frontend-envelope.schema.json; message 1..4000 chars; stale profile 409. `statements` is the only assistant factual output. `provider` status may be unavailable while safe statements remain. No mutation tool and no action inferred from free text |
| GET /api/plans | none | `{plans:PlanProgress[]}` |
| POST /api/plans | `{plan:PlanProgress,idempotency_key:string,design?:object}` | persisted plan wrapper; server owns plan ID; same key/body retries only |
| POST /api/pathway-preview | `{role_id:string}` | unsaved pathway preview, not an executed plan |
| GET /api/plan-designs | none | `{designs:object[]}` |
| GET or POST /api/learning-resources | POST `{topic_ids?:string[]}` | official resource options; unverified effort stays null |
| POST /api/company-explorer | `{employer_id:string,role_id?:string}` | source-backed company result; unknown requirements explicit; main recommendations unchanged |
| GET /api/proposals | none | `{proposals:[{preview:{request,proposal_id,origin},preview_hash,status}]}`; status pending/rejected/applied; origin inferred/scheduled/market_event |
| POST /api/proposals | `{request:ActionRequest}` | `{preview,preview_hash,status:"pending",target_changed:false}`; validates feasibility, no target mutation |
| POST /api/direct-action | `{request:ActionRequest,idempotency_key:string}` | `{action:Action,target:Profile|PlanProgress}` persisted result; only send after a specific scoped user instruction |
| POST /api/proposal-decision | `{proposal_id,decision:"approve"|"reject",preview_hash,expected_state_version}` | reject `{status:"rejected",target_changed:false}`; approve persisted `{action,target}`. Exact preview approval; stale/changed scope rejected |
| GET /api/action-history | none | `{history:Action[]}` persisted audit results; no standalone jobs endpoint |
| POST /api/undo | `{action_id,expected_state_version,idempotency_key}` | persisted inverse action result; only reversible supported diffs |
| GET /api/agent-settings | none | saved settings + version (404 if absent) |
| PUT /api/agent-settings | `{settings:{enabled:boolean,check_time:"HH:MM"},expected_version:string|null}` | persisted settings; profile timezone applies; no pause/delete/general scheduling API |
| GET /api/agents | none | `{events:[{id,kind,status,attempts}],notices:object[],deployment_scheduler_verified:false}`; statuses pending/processing/retry/failed/processed; notices contain actual persisted analysis/proposal, not executed target success |

ActionRequest = `{kind,target_id,expected,diff:ActionDiff[],reason,evidence_ids?:string[]}`. Kinds: complete_task, reschedule_task, update_profile, change_goal, replace_plan; paths/feasibility checked by backend. `expected` is target's current version (Profile.version or PlanProgress.state_version), not the chat context_version. Approval uses the returned preview hash and preview.request.expected_state_version. Idempotency keys are nonempty strings ≤200 chars; keep the exact same body/key for retries; a different scope conflicts. Proposal creation itself has no idempotency key, so do not blindly retry it. Chat also has no idempotency key and consumes budget per call. Show action success only from a successful persisted response; refetch affected profile/plans/events.

## Errors, safe presentation and privacy

Errors: `{code:string,request_id:string}`; 401 unauthenticated, 404 missing/unowned/unsupported, 409 stale/version/scope/idempotency conflict, 413 oversized request (128KiB transport), 415 unsupported intake type, 422 shape/contract/feasibility, 500 internal. Never render raw exceptions. Refresh on 409 and require review of changed proposal; don't silently reapprove. On timeout reconcile GETs before mutation retry; preserve original idempotency key. Provider retry/budget is server controlled; no extra automatic browser loop.

Render chat statement.text as text, not model HTML. Categories are external_fact, user_reported, calculated_assessment, proposed_action, limitation. Backend resolves Source records/HTTPS URIs; model selects opaque IDs only. Preserve period/status/type/scope, nullable dates and edition labels. Do not display raw public-context personal_score, rank, internal matrices or ordinary ranking scores merely because a reference endpoint supplies them. Unavailable forecast means unavailable, not zero. Citation presence alone is not proof; C verifies closed passages and A recomputes source derivations.

Policies: `minder-grounding-privacy-v1`; evidence `minder-evidence-passage-v1`, `personal-current-evidence-v2.1`; personal fit `personal-role-fit-v3-provisional`. Original N01 is not enabled. The backend sends only bounded redacted question and canonical passages/opaque IDs to Groq; no token/full profile/CV/ranking matrix. See prior C grounding/privacy refinement for plaintext SQLite history/no expiry and provider-account settings explicitly unverified. Retrieved text never authorises tools. F must retain normal safe link rendering and should not add provider calls or duplicate stores.

## Reproducible examples

`examples.json` is generated by `apps/backend-api/tests/export_frontend_contract.py` against the exact recorded backend commit. It uses a fictional synthetic user and actual committed source services, with mocked provider selection clearly labelled. No session token is exported. Chat wrappers validate against the local export envelope schema; profile/source/MarketEvidence/EvidencePassage validate against shared schemas and semantic validators. This export does not claim real-provider or product-browser acceptance. CL3 refresh will separately report real calls. F can implement unsupported transcript history as an explicit unavailable capability, or request a separately authorised shared contract from A; do not invent an endpoint.
