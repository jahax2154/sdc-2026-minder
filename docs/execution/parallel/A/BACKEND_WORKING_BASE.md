# Frontend working base — AC4.0

Repository: https://github.com/jahax2154/sdc-2026-minder
Branch: session/a-personal-integration.
Real-provider-tested runtime checkpoint:
87c80cf69b9da27d9bffbcf2049fc4c2b54d1493.
The AC4.0 commit containing this handoff adds input provisioning and isolated B
scenario integration; its full published SHA is reported by A. Runtime scoring
and endpoint implementations remain those tested at AC2.

This is an available Git starting point and local API contract boundary. There is
no published/hosted API URL or deployment. C owns the authoritative endpoint/schema
export at docs/execution/product/llm/FRONTEND_CONTRACT.md; CL1 is pending at this
checkpoint. F can prepare the shared client now, then bind C's actual examples.
No backend duplication or new provider client is needed.

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

Provider access: configure authorised server-only GROQ_API_KEY and optional
GROQ_MODEL in the checkout's ignored owner-only regular .env.groq.local, using the
existing safe loader. Do not expose them to the frontend. A's current authorised
binding works; no new key is required for A. A's verified noncredential model ID
is recorded in AC2.json. Without provider access, the API returns an honest
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

C's current closed grounder verifies Bosch derivations. New published/shortage/
sector facts work in backend/UI, with A EvidencePassage v1 available. CL2-CL3
consumer/real-provider proof is still pending; do not label these model claims
already supported. A will publish an updated base after committed integration.
B simulations remain isolated: no change to ordinary recommendation/source counts
or default forecast availability. Missing historical forecasts do not block F
client/source/design work.

See AC2.json for real evidence and AC4.0.json for provisioning verification.
