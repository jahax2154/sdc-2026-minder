# A-UX2 — live local bot identity/history search integration

D committed d734d95cf68cb4945562bd9166714798edc2fb23, integrated by normal merge
a4a269d343954541183c8c929a8ed62dc5daae58. Exact producer changed paths and focused/
combined160-test evidence are D/D_UX1_BOT_AND_SEARCH.md. Sole D-owned persistence
files, schema7 unchanged; no migration, second database or new bot identity.

A stopped only its verified owned54681 runtime and restarted the same private
environment/SQLite on8111API/9111UI with existing explicit worker. Startup/health
revision a4a269d343954541183c8c929a8ed62dc5daae58; actual Qwen model unchanged.
F's runtime/worktree was not modified by A. Localhost remains local, not hosted.

Actual A WSGI/schema integration passed two synthetic owners: read-only defaults,
trimmed saved display name, canonical avatar allowlist, stale/foreign versions,
unchanged Profile/schedule/singleton. A fixture creates102visible messages through
the actual conversation API with an explicit software handler; search finds message
101 beyond the default100-message page. Unicode casefold, literal%, dedup/pagination,
deleted/foreign/Mindbot exclusion and zero action replay pass. This is backend
integration, not an actual model conversation or live login.

Actual restarted A HTTP listener separately passed trimmed identity save/reload,
401without auth, stale409, two-owner identity and Unicode title-search isolation,
same Profile/singleton, no schedule creation and0actions/provider-turn requests.
Exact25Home/brief/25avatar hash and strict public contract checker also passed.
Public routes now implemented on A: GET/PUT `/api/product/bot-preferences` and
POST `/api/product/conversations-search`. F may use the committed schema unchanged.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_ux_state_integration.py
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_ux_http.py
```

Private sanitized reports: morning/ux-state-integration.json and ux-http.json.
Synthetic conversation/profile/state data remain in disposable/A-local DBs, not Git.
No credentials were copied, logged or put in browser processes. Source inputs and
other lanes remain untouched. Runtime data was preserved across the own-process
restart; this does not certify hosted durability, live Clerk or judge deployment.

F remains sole UX3/4/5/6 writer and is testing its committed D dependency separately.
A will integrate its committed frontend slices, inspect actual A rendering and run
the final combined journey. Current frontend Home/customization/search completion
is not asserted by this backend checkpoint. Actual Home mappings/missing projections
are [HOME_ACTUAL_READ_MAP.md](HOME_ACTUAL_READ_MAP.md); preserve separate display
identity, automation status, canonical progress and no fabricated template data.
