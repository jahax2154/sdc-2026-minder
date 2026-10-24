# A-UX0 — approved Home/assets and independent D/F contracts

Base:582f3fda05abb4c5a4cbcac306bc087f5f5809ce. New authority is the unchanged
`docs/Minder_Frontend_Final_Repair_and_Home_Gate.md`, Revision1. F remains sole
frontend owner. No F shell/client/style file is changed by this checkpoint.

## Assets released now

`docs/Minder_Home_Package/` contains the exact24source/reference files from the
original checkout; [HOME_ASSET_HANDOFF.json](HOME_ASSET_HANDOFF.json) records each
hash and the exact brief. Read README, docs/DESIGN_CONTEXT.md and FRONTEND_LOGIC.md.
Its demo fixtures/localStorage are not production records. New gate72px global
rail overrides standalone Home's238px mock rail; keep current fonts/framework.
No sample completed tasks, matches, names or ON state are copied as real state.

All25approved avatar files are ALREADY tracked under
`docs/minder-ui-html-previews/assets/`: nimo PNG and frog/heart/puff/star SVG, each
blue/lavender/lime/rose/yellow. [BOT_AVATARS.v1.json](BOT_AVATARS.v1.json) is the exact
ID/source/hash allowlist. IDs are file stems, e.g.nimo-blue/frog-rose. F copies only
chosen approved files into its owned static root; source hashes must remain equal.
Use no remote URLs, generated art or upload flow. Default display is **My Bot**,
default avatar **nimo-blue**; never hardcode Nimo as every user's name.

## D implementation approval — start independently

A registers routes below and publishes executable definitions in contracts.schema.json.
They remain unavailable until D's committed implementation declares OPERATIONS.
This checkpoint is a dependency release, not evidence that settings/search already run.
D owns bot_preferences.py/test_bot_preferences.py plus its existing conversation/
schema/tests; ownership records the added exact files. Reuse Store kind bot_preferences,
owner key owner, existing settings document/version semantics; no second DB/bot/profile,
new migration or changes to agent_settings. D alone decides any necessary migration.

### Bot identity

GET `/api/product/bot-preferences`, empty body, returns:

```json
{"contract_version":"bot-preferences-v1","configured":false,"preferences":{"display_name":"My Bot","avatar_id":"nimo-blue","version":null}}
```

GET defaults are read-only: do not create a row, conversation or daily schedule.
PUT same route:

```json
{"display_name":"Study Buddy","avatar_id":"frog-rose","expected_version":null}
```

Returns same result shape, configuredtrue, opaque stored version. Normalize the
string with strip BEFORE validating BotPreferencesWrite, then require1..40Unicode
codepoints/no C0/C1 controls. Reject empty, wrong type, unknown keys/avatar IDs and
URLs. No client owner. expected_version must match current preferences version,
null only for first save; stale ->409. No automatic write retry. An uncertain save
requires reloading current identity/version; preserve the draft for explicit recovery.
Custom name is plain escaped display data, never a system instruction, auth claim,
new conversation ID, skill or schedule. Rename/avatar save must leave singleton,
Profile, tasks, permissions and automation state/version unchanged.

F can wire the GET/PUT adapter now but must display a local error if unavailable,
not claim browser-only customization is persisted. Cancel writes nothing. Apply
successful saved identity to panel/page/sidebar/Home with user-scoped cache clear.
configured tracks actual saved identity; enabled/status/next_run remain separate
actual agent-settings reads, not implied by customization.

### Owned Minder history search

POST `/api/product/conversations-search` to D conversations dispatcher:

```json
{"query":"notebook","limit":20,"offset":0}
```

query required string<=200, strip; limit1..50 default20; offset0..100000 default0.
Use POST so private search text is not put in URL/query logs. Never log its value.
Literal case-insensitive substring search of this owner's ACTIVE MINDER titles and
persisted visible messages: user.text, assistant.answer and visible statements.text.
No raw response JSON/provider IDs/private metadata search; no model/action invocation.
`%`/`_` are literals, not SQL wildcards. Empty query lists all owned active Minder.
One row per conversation, ordered updated_atDESC,idASC. Deleted/Mindbot/foreign
records excluded, including messages beyond the first opened history page.

Response (normal existing conversation metadata, no message snippets/full transcripts):

```json
{"contract_version":"conversation-search-v1","query":"notebook","search_scope":"title_and_visible_messages","conversations":[],"offset":0,"limit":20,"has_more":false,"next_offset":null}
```

next_offset=offset+returned_count iff has_more, otherwise null. Existing GET list
and open(after_sequence/limit) remain compatible. Offset pagination is acceptable
for this prototype; refetch page0 after sends/deletes. It is not a snapshot cursor
under concurrent updates. F debounces, cancels/ignores stale reads and scopes cache
by user/query. Search response never replays a saved turn or writes an action.

## Focused committed handoff requirements

D: verify both exact public result schemas, defaults/no-write, trim/limit/control
validation,25allowlist, stale versions, two-user isolation/restart, unchanged
Profile/singleton/schedules; title and old-message matches, literals, dedup/order/
pagination, deleted/foreign/Mindbot exclusion,0provider/actions. Commit and push
only owned backend files; give A/F full SHA/dependencies and actual checks.

F: merge this A commit normally (no cherry-pick of partial dependencies), continue
UX1/2 while D implements, then consume D committed handoff/A integration. All new
UI remains F-owned. Home uses existing overview/profile/direction/plan/progress/
conversation/settings reads; send exact minimal missing E read fields, no parallel
aggregate store or client scoring. A owns final integration and actual9111 acceptance.

## Verification at this contract checkpoint

Exact25Home/brief hashes and25existing avatar hashes verified; strict schema accepts
all25IDs and rejects unapproved URLs/paths, blank/control/overlong normalized names.
Registry exports correct D ownership and unavailable status until implementation.
`checks/check_frontend_ux_contracts.py` passes. Existing four bootstrap/WSGI contract
checks pass2.460s; `git diff --check` passes. No provider call, DB migration, F edit,
private screenshot import or runtime acceptance claim accompanies this source release.
