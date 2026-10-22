# Local integration release handoff

This is a verified local API/UI/service release candidate, with explicit numerical,
data and provider limits. The current task authorises no deployment or Git push.
Use I2.4-R01 for current readiness; historical I2.4 predates the final B/C handoffs.

## Reproduce in Session A

The existing interpreter and pinned read-only inputs are reused. No dependency
installation occurred. Source the **A** `.env.local` in the required worktree;
it selects current-worktree `ml/src`, A ports, and an A-only database/artifact path.
For a new machine, restore the 13 inputs at repository-relative paths using
`source_snapshot.v1.json` hashes and the existing source manifest/attribution.
Do not assume those untracked bytes are included in a Git clone.

```sh
source .env.local
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli serve-web
```

This serves the real A/B/C application on loopback API 8101 and UI 9101, reusing
C's committed static/API web wrapper with A's source-service binding. It verifies
source bytes, opens the reserved A SQLite file, applies C migrations 1–3 and
creates migration 4's provider budget table on the first budgeted chat/worker call.
It loads 1,016 occupational references / 910 supported candidates and uses the
committed B snapshot and source registry; there is no fixture-provider fallback.
Health: `GET /api/health`, integration mode `local_source_services`. API-only
`integration_cli serve` remains available. C's runtime database guard is unchanged;
do not use its C-only launcher to open A's database.

Create a local session with `POST /api/session`, then use its bearer capability
for the documented C routes. Capabilities and database files stay local/ignored.
`PUT /api/profile` saves a Profile DTO with an expected version. `GET
/api/career-context` exposes the supported unranked catalogue. `POST
/api/career-context` takes explicit `selected_role_ids` / registered
`selected_skill_ids` for a bounded source-grounded view. `POST /api/chat` takes
the selected view and expected profile version. Selection is not ranking.

For a fresh, synthetic real-HTTP acceptance run:

```sh
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli acceptance \
  --output ml/artifacts/session-a/<new-evidence-directory>
```

It starts and shuts down its own loopback server, creates an isolated A database
and exercises real source-backed services/persistence/actions. It never writes
production state. The previous passing run is `i2.2-http-v4/evidence.json`.

To reproduce the latest actual HTTP and Chromium UI acceptance, reuse an
available Playwright library/browser and run when A's reserved ports are free:

```sh
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-web \
  --output ml/artifacts/session-a/<new-ui-evidence-directory> \
  --playwright-module /private/tmp/minder-c-ui-check/node_modules/playwright \
  --browsers-path /private/tmp/minder-c-browser
```

Those temporary dependency paths were available for this run; no installation or
application build occurred. On another machine supply available equivalents.
The adapter replays C's committed tests with only ports, evidence destinations
and report port labels adjusted into A. Original test hashes are recorded.
All app/UI source and actual requests remain unchanged; no network mocks.
Passing evidence is `resume-i2.2-r01-v1/integration-evidence.json`, with a visually
inspected synthetic screenshot. Its own servers shut down after verification.

For the bounded worker check, retain A's `MINDER_DB_PATH` and run:

```sh
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_app.worker --once
```

This is a local deterministic tick. Deployment supervision, wake/sleep and a
real unattended scheduled wall-clock run remain unverified. Run no paid jobs.

## Verified behaviour and limits

The API supports saved intake, draft clarification, real occupational-reference
assessment, scoped company exploration, pathway previews, persisted plans,
direct specific actions, exact proposal approval/rejection, stale-version
conflicts, retries, undo of supported scalar edits and activity/mastery
separation. Source references, dates, current observations and forecast
unavailability reach the public boundary without internal market matrices.

N01 is pending/inactive. There is no numerical personal role-fit, preference
penalty or blended recommendation ranking. Source skill IM/LV ratings have no
accepted occupation-to-person proficiency rubric. All competence gaps remain
unknown where that rubric is absent. A completed course/task is not mastery.

Current market counts describe 39 inspected Bosch Malaysia advertisements,
with partial title/technology dictionary coverage. They are neither national
demand nor quarterly inflow. Next-quarter role and skill forecasts are
unavailable: there is no compatible quarterly source history or selected real
forecast model. Mathematical Ridge/XGBoost runs remain non-promotable; their
metrics do not establish personal-fit or forecast accuracy.

Groq probe returns `provider_credentials_missing`; `GROQ_API_KEY` and
`GROQ_MODEL` are absent. Chat returns bounded unavailability and factual service
statements. Configure credentials privately and verify model entitlement and a
grounded call before claiming provider readiness. No secret value was inspected
or recorded. B's final `63b45ab4ce572b2cf750ed9f527f33b1f7b94a21` and C's final
`c5de33bcd2f27a537ca57b30e1e4cba859098e80` handoffs are now reviewed and integrated.
The current application/UI works locally with these explicit provider, scoring,
forecast, company-criteria and pathway-resource limitations.

No Replit configuration/deployment was found or verified. The current user's
explicit no-deploy/no-push instruction controls release actions. Before any
later authorised deployment, the release owner must select actual hosting and
durable storage, wire the UI to this same API, verify authenticated owner
isolation and source/artifact access, configure Groq privately, and observe
worker operation. No live URL, deployed revision or competition compliance is
claimed by local tests.

## Evidence

`I2.1-R02.json` records 152 passing ML tests, 20 distinct backend tests, preserved
source hashes, both exact owner revisions and migrations 1–4. `I2.2-R01.json`
records actual HTTP/Chromium checks, provider unavailability and no network mocks.
`N01_REVIEW.md` identifies the unchanged pending proposal and decision scope.
`A3.1.json` retains personal-service coverage, mathematical learner status and
blockers. Exact local package versions remain in `I2.3.json`; current compatibility
and provider probes are in I2.1-R02. No unrelated data, model weights,
credentials or SQLite files are committed or newly backed up externally.
