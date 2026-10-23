# Frontend working base — AC4.0

Repository: https://github.com/jahax2154/sdc-2026-minder
Branch: session/a-personal-integration.
Final tested runtime checkpoint:
23f3f057132889b2f62e72657a9f4678042bc0e0.
The final AC4.2 documentation freeze follows this source; A reports its exact
remote SHA after publication. C final handoff362316351ebe90b31c533eb75cff46a851808314
and B final handoffd9ffd4f3cc7625c736ea081c52da3c1122b21c08 are integrated with normal history.

The authoritative C endpoint/schema export is
[FRONTEND_CONTRACT.md](../../product/llm/FRONTEND_CONTRACT.md), with schema-valid
examples. A accepted its six source passages against pinned services. Four typed
families now work in actual A chat and scheduled notices; AC2-R01/AC4.1 record
real provider/TCP HTTP/source/action/clock/privacy acceptance. No scorer or
evidence-scope change. F can wire this contract now.

This is a published Git starting point plus a loopback development service, not a
hosted remote API or deployment. Local entry http://127.0.0.1:9101/ and /api/ are
running on this Mac. Remote F uses its approved same-origin proxy/backend setup.

## Start the existing backend in a permitted development checkout

For a remote teammate, use a fresh checkout at the published SHA. Do not modify
A/B/C branches; record and use your assigned frontend feature branch. Existing
A uses its prepared interpreter and config; do not repeat its environment setup.

A fresh machine needs Python3.9+ and the existing foundation dependencies.
Example commands for a new permitted development checkout only:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r ml/requirements-foundation.txt
    .venv/bin/python docs/execution/parallel/A/checks/provision_dev_inputs.py --source-root "$MINDER_SOURCE_PACK"

MINDER_SOURCE_PACK is an authorised existing pack directory containing the 13
raw/derived paths pinned in docs/execution/parallel/source_snapshot.v1.json. It is
not a URL, credential file, model artifact directory or C runtime. Obtain a
permitted copy through the team's source provisioning channel; do not publicly
upload raw inputs or infer redistribution permission from this helper. On this
Mac the existing G0 shared snapshot supplies it. The old absolute manifest path
is historical provenance, not a requirement on another machine.

The helper checks every source hash and all existing destinations before any copy,
copies only missing pinned files, sets new files read-only and refuses mismatched
existing inputs/symlinks/outside-worktree destinations. It never stages inputs.
Without --source-root it only verifies existing inputs. A Git clone alone does
not include these bytes; no public input download/bundle is fabricated here.

Provider access: configure authorised server-only GROQ_API_KEY and
GROQ_MODEL=qwen/qwen3.8-27b for the tested A profile in the checkout's ignored owner-only regular .env.groq.local, using the
existing safe loader. Do not expose them to the frontend. A's current authorised
binding works; no new key is required for A. Its verified noncredential model ID
and the original-model failure history are recorded in AC2-R01.json. Without provider access, the API returns an honest
unavailable state. No raw real CV/profile is needed to verify the prototype.

    export PYTHONPATH=ml/src:apps/backend-api
    export MINDER_ARTIFACT_DIR="$PWD/ml/artifacts/session-a"
    export MINDER_DB_PATH="$PWD/ml/artifacts/session-a/runtime/dev.sqlite3"
    export MINDER_API_PORT=8101
    export MINDER_UI_PORT=9101
    .venv/bin/python -m minder_ml.intelligence.integration_cli serve-web

Use the environment's existing interpreter instead of .venv on A. No application
build is required. Data migrations are idempotent against this isolated SQLite.
The command stays in the foreground; it does not start an unattended scheduler.
A currently keeps this loopback development base running with isolated database
ml/artifacts/session-a/closure-runtime/dev.sqlite3; health verified at /api/health.
This is a local handoff service, not a remote hosting/deployment claim.

Local acceptance UI: http://127.0.0.1:9101/
Same-origin API base: /api/ (absolute local listener http://127.0.0.1:8101/api/).
F must use relative/proxied same-origin routing, not hardcode this Mac's loopback
address in a remote frontend. There is no CORS/cookie auth or production identity
claim. Remote hosting/auth/proxy/scheduler remain separately owned release work.

## Existing implemented operations, read directly from api.py

| Method/path | Binding |
| --- | --- |
| GET /api/health | Public health/integration mode |
| POST /api/session | Creates local anonymous bearer capability; token stays private |
| GET/PUT /api/profile | Owner profile; PUT uses expected_version |
| POST /api/chat | message, expected_profile_version, optional selected_role_ids/selected_skill_ids |
| GET/POST /api/plans | Persisted owner plans; creation requires idempotency_key |
| POST /api/direct-action | Explicit request plus idempotency_key; exact persisted result |
| GET/POST /api/proposals | List or create concrete preview; creation does not execute |
| POST /api/proposal-decision | proposal_id, decision, preview_hash, expected_state_version |
| GET /api/action-history | Persisted action result/history |
| GET /api/agents | Owner events, notices and job state |
| GET/PUT /api/agent-settings | Actual enabled/check_time controls with expected_version |
| GET/POST /api/career-context | Current recommendation/profile context; no forecast invention |
| POST /api/role-evidence | role_id; optional trace_id and expected_profile_version/view_role_ids |
| GET /api/source-market-catalogue | Native dated source categories; no ranking inference |
| POST /api/source-market-context | Explicit MASCO code/version or evidence_ids |

All owner operations use Authorization: Bearer <private session token>. Never put
tokens in public fixtures, URLs or logs. Expected versions, preview hashes and
idempotency keys are capability/state bindings; frontend buttons do not bypass
them. 401/404/409/422 and unavailable provider/source states need explicit handling.
The current API is synchronous JSON, with no validated streaming contract.
No general conversation-history reader/job-stream endpoint is promised by this
inventory; C's actual export must identify unsupported operations honestly.

Sources are backend-resolved typed facts. Render safely as text; no model HTML.
Keep current/historical periods, units, null MyCOL dates/edition, category proxy
and related-group/child restrictions. Ordinary numeric ranking values remain
hidden in the product presentation. Persisted actions and source evidence are
different from the LLM's language-assisted opaque-ID selection.

## Readiness and remaining owner handoffs

A real discovery/chat/native tool, direct action, proposal reject/approve and
actual upcoming-minute owner-scoped worker passed in AC2. The real Chromium privacy
check passed with source binding, unavailable forecast, no false action/profile
mutation and no page errors. This verifies the repository local prototype only.

C's typed bridge now recomputes all four accepted source families before ledger
storage and after load. A's worker adapter passes its real services into that same
boundary. Current/forecast, source units, category-proxy and related-group/child
limits remain explicit. No raw profile/CV/ranking matrix is sent as facts.

C's own original-model final HTTP report remains limited as historically recorded;
A verified and selected accessible Qwen using the same authorised key, unchanged
cap/validation/authority and no semantic retry. All four families passed real A
selection/source reconciliation, TCP HTTP and actual scheduled output checks.
Invalid output/unavailability remains a supported safe state for F.

B simulations stay isolated from normal evidence, coverage and forecasts. Missing
history does not block F frontend work. Intended product frontend/browser acceptance,
production authentication/hosting/storage and continuous scheduler remain separate
F/release responsibilities. Only repository prototype privacy/source rendering was
verified here. See AC4.1.json and AC4.2.json.
