# Minder local application

Python 3.9+ stdlib WSGI + SQLite; shared `jsonschema` dependency already in the foundation environment. No new root packages or framework bootstrap. Owns profile/intake, grounding, company exploration, plans/progress, scoped actions, agent worker and browser API. Real A/B source services are bound by `minder_app.runtime`; `Application(Store(...))` without services is explicitly unavailable, never an implicit fixture.

From repository root:

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_app.dev
```

Local UI `http://127.0.0.1:9103`; API `http://127.0.0.1:8103`. Both use only C's assigned `MINDER_DB_PATH` under `ml/artifacts/session-c/`. Runtime refuses other DB namespaces. To run just the API, replace `minder_app.dev` with `minder_app.api`. Listeners are local development, not a deployment. Anonymous opaque bearer capability is held in browser sessionStorage; token hash only in DB. Do not share tokens. Production login, expiry/recovery, HTTPS and durable hosting remain A release work.

Migrations apply transactionally on app/worker construction: 1 documents/history/sessions/drafts, 2 authorities/proposals/executions/audit, 3 events/notices, 4 provider call budgets (on first bounded provider use). Plan-creation idempotency is an additive table on first create. Migrations are additive; no production database was modified. Preserve the database file and WAL while running. Local files are ignored, not committed/backed up by this task.

```sh
# Separate supervised worker process; enabling a UI check does not launch this.
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_app.worker
# One bounded tick for diagnostics:
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_app.worker --once
# Local tests (temporary isolated DBs):
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests -v
# Actual HTTP, committed A/B sources, synthetic users in C's dev DB:
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" apps/backend-api/tests/http_acceptance.py
# Real provider access check, no response text/credentials printed:
"$MINDER_PYTHON" -m minder_ml.intelligence.groq_adapter
```

Provider variable names: `GROQ_API_KEY`, `GROQ_MODEL`, optional `MINDER_LLM_DAILY_LIMIT` (default 20 calls/user/UTC day, clamped 1–100). No model default is invented; probe discovers available configured models and requires an explicit selection. Tests of transport errors use mocks and do not establish live access. Runtime names: `MINDER_DB_PATH`, `MINDER_API_PORT`, `MINDER_UI_PORT`, `MINDER_PYTHON`, `PYTHONPATH`. Agent time and enable state are saved per user; timezone comes from the profile. Deployment scheduler is explicitly unverified.

API examples (all non-health/session routes require `Authorization: Bearer <private-token>`):

- `POST /api/session {}` returns a local user capability. `GET /api/health` returns integration mode.
- `PUT /api/profile {"profile":<shared Profile>,"expected_version":null|<saved version>}` is a direct structured edit; server owns profile ID. `GET /api/profile` reads only the caller's profile. Public intake accepts explicit-user/document-claim/synthetic evidence, never certifies competence.
- `POST /api/intake {"text":"…","channel":"chat"}` or `filename:"cv.txt",content_type:"text/plain"` stages a draft; it cannot edit profile. UTF-8 TXT only, 64 KiB max. Unsupported files return explicit errors.
- `POST /api/roles {"query":"software","offset":0,"limit":20}` browses the full catalogue in catalogue order. Clear query to restore scope. `POST /api/role-requirements {"role_id":"onet:15-1252.00"}` reads source requirements.
- `GET /api/career-context` returns all supported unranked candidates. `POST /api/career-context {"selected_role_ids":["onet:15-1252.00"],"selected_skill_ids":["source-term:python"]}` creates an explicit bounded exploration view. Max three roles and three registered skill IDs; arbitrary evidence subjects are not skill market targets.
- `POST /api/chat {"message":"Explain next quarter","expected_profile_version":"…","selected_role_ids":["onet:15-1252.00"]}` selects application-grounded facts; model prose/weights/actions cannot become output/mutations. Snapshots retain profile/policy/model/source versions. No selected view means coverage/clarification rather than a first-N fake ranking.
- `POST /api/pathway-preview {"role_id":"…"}` returns an unsaved source-criterion preparation design. `POST /api/plans {"plan":<PlanProgress>,"design":<optional annotations>,"idempotency_key":"…"}` is explicit selection. `GET /api/plans`, `/api/plan-designs` share persisted state. Unknown effort/resources/feasibility are explicit; no employer requirements invented.
- `POST /api/company-explorer {"employer_id":"bosch","role_id":"onet:15-1252.00"}` reuses B's dated Malaysia summary; criteria unavailable are distinct from generic A assessment. Intel has only a checked official entry. No broad employer coverage/current vacancy guarantee.
- `POST /api/direct-action {"request":{"kind":"complete_task","target_id":"<plan-id>","expected":"<plan-version>","diff":[{"path":"/tasks/<task-id>/state","before":"proposed","after":"completed"}],"reason":"User clicked complete"},"idempotency_key":"<unique-key>"}` executes one trusted scoped UI instruction without redundant approval. IDs are opaque. Reschedule paths `/tasks/<id>/scheduled_at` require existing scheduled state, known effort/capacity and valid graph/deadlines. Profile preference paths `/preferences/role/<id>` or `/preferences/industry/<id>` use before/after states; null removes a preference. Existing constraints use `/constraints/<id>/value`.
- `POST /api/proposals {"request":<same request shape>}` previews without target mutation. `GET /api/proposals`; `POST /api/proposal-decision {"proposal_id":"…","decision":"approve"|"reject","preview_hash":"…","expected_state_version":"…"}` binds exact preview/version. No bare 'yes' or caller-supplied approved state. `GET /api/action-history`; `POST /api/undo {"action_id":"…","expected_state_version":"…","idempotency_key":"…"}` inverses reversible scalar changes, preserving completed work/history.
- `PUT /api/agent-settings {"settings":{"enabled":true,"check_time":"08:00"},"expected_version":null|"…"}` records daily intent. `GET /api/agent-settings`, `/api/agents` expose saved configuration/events/notices. Worker auto-analysis only proposes; failures retry at most three times. `agents.market_event` is a server-only validated-source/relevance hook, not a public market assertion endpoint.

All errors use safe `code` and `request_id`; stale state returns 409, missing identity 401, other-user records 404, bad contracts 422. No raw market-score matrix in consumer routes. N01 remains inactive: 910 supported source candidates, no numerical role-fit scores or rankings. Current employer counts are a bounded observed active-ad snapshot, not national demand or quarterly inflow. Both role/skill forecasts can remain unavailable.
