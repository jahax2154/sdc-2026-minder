# D-UX1 — persistent display identity and owned Minder search

Status: passed for the bounded local backend slice. Authority/dependency:
A c7d6ebfb3ad60e13f07b03bb20325be28926bfc1,
A_UX0_BACKEND_AND_ASSETS.md and Minder_Frontend_Final_Repair_and_Home_Gate.md.
F retains every frontend file; A published exact schemas/routes/avatar hashes first.
No root/shared/A/F/E file was edited by D. SQLite schema remains7; no migration,
second bot/profile/conversation database, provider call or deployment.

## Exact bot identity interface — implemented

GET /api/product/bot-preferences, {}:
```json
{"contract_version":"bot-preferences-v1","configured":false,"preferences":{"display_name":"My Bot","avatar_id":"nimo-blue","version":null}}
```
Defaults come from A's BOT_AVATARS.v1.json, validated against canonical schemas.
GET creates no preference/profile/conversation/schedule row. Returned copies do not
mutate server defaults. Actual saved identity returns configuredtrue and an opaque
version. No enabled/automation state is implied by configured.

PUT same route:
```json
{"display_name":"  Study Buddy  ","avatar_id":"frog-rose","expected_version":null}
```
Returns the same envelope with configuredtrue, trimmed display_name and persisted
version. Uses canonical BotPreferencesWrite/BotPreferencesResult definitions,
including25approved avatar IDs,1..40Unicode name codepoints and no C0/C1 controls.
Unknown fields/IDs/URLs, blank/overlong/wrong types rejected422; unauthenticated401;
stale expected_version409. null is only first save. Same values/current version
are a no-op; stale writes are never auto-retried. After uncertain save, F reloads
current version and explicitly reconciles draft intent. Cancel sends no write.

Backing record is existing Store.documents/history kind bot_preferences/id owner.
A's server identity determines owner, never request data. Save changes only that
record. Profile, plan, same Mindbot singleton, permissions and agent_settings/version
remain unchanged. Name/avatar are plain display data, never model instructions,
new bot IDs or schedule authority. F uses escaped rendering and user-scoped cache.

## Exact owned search interface — implemented

POST /api/product/conversations-search:
```json
{"query":"notebook","limit":20,"offset":0}
```
query required<=200, strip; limit1..50/default20, offset0..100000/default0.
Uses A's canonical ConversationSearch and ConversationSearchResult definitions.
Response shape:
```json
{"contract_version":"conversation-search-v1","query":"notebook","search_scope":"title_and_visible_messages","conversations":[],"offset":0,"limit":20,"has_more":false,"next_offset":null}
```
Each conversation is the existing metadata DTO; no snippets/full messages/private
raw JSON are exposed by search. Literal Unicode casefold substring matches active
owned Minder titles, persisted user.text/assistant.answer and visible statements.text.
It searches ALL persisted messages, including beyond loaded/opened pages. Internal
provider/status/outcome metadata is not searched. Percent/underscore are literal,
SQL input bound parameters; empty query lists all active owned Minder.

Deduplicated conversations order updated_atDESC/idASC. next_offset exists only if
has_more; offset pagination isn't a concurrent snapshot cursor. Deleted, foreign
and Mindbot histories are excluded. Existing list/open unchanged. Read-only SQL
and an ephemeral casefold function in the same Store connection; no new search
index/store, provider/worker/action callback, query logging or saved search records.
F debounces/cancels stale queries and refetches first page after sends/deletes.

## Actual checks and handoff

15focused bot/conversation tests passed: default/no-write/copy isolation, all25
avatars, Unicode normalization/bounds/control/unknown keys, stale version and8
concurrent first writes(one winner), owner isolation/restart, unchanged canonical
Profile/plan/Mindbot/schedule; title/text/citation/older-than100-message-page matches,
literal wildcards/injection-like text, Unicode Straße/RÉSUMÉ casefold, dedup/order/
pagination, deleted/foreign/Mindbot exclusion and no callback replay.

Combined160 backend tests ALL passed under E's published Python3.12 runtime,
PYTHONDONTWRITEBYTECODE=1 (read-only environment), no SDK/PDF skips. A's exact
25avatar/25Home-brief hash/schema/registry checker passed. D's actual private-file/
canonical-action/Worker/fresh-child-process acceptance runner also passed after
adding persisted bot identity+owned search reads, with schedule unchanged. Identity
and model portions remain explicitly software fixtures, not live hosted auth.

Reproduce:
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests /private/tmp/minder-e-auth-py312/bin/python -m unittest test_bot_preferences test_conversations
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m unittest discover -s apps/backend-api/tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python docs/execution/product-v2/checks/check_frontend_ux_contracts.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python docs/execution/product-v2/D/check_morning_persistence.py
```

No new runtime configuration dependency: current Dockerfile already copies both
minder_app modules and docs/execution/product-v2 (schema/manifest). F copies approved
avatar bytes into its owned static directory. Actual mounted host/login/deployment
limits from MD3 remain unchanged/unverified; no new UI browser proof claimed by D.
Unrelated raw/derived source inputs remain untracked/untouched and not backed up.
Publish only assigned session/d-profile-state; return exact SHA to A/F for live UI
integration and their owned acceptance, never deploy or update main from D.
