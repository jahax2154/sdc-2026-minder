# Local integration release handoff

This is a verified local API/service release candidate, with explicit numerical,
data, provider and UI limits. No deployment or Git push is authorised/performed.
Use the checkpoint containing this document and the later I2.4 manifest together.

## Reproduce in Session A

The existing interpreter and pinned read-only inputs are reused. No dependency
installation occurred. Source the **A** `.env.local` in the required worktree;
it selects current-worktree `ml/src`, A ports, and an A-only database/artifact path.
For a new machine, restore the 13 inputs at repository-relative paths using
`source_snapshot.v1.json` hashes and the existing source manifest/attribution.
Do not assume those untracked bytes are included in a Git clone.

```sh
source .env.local
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli serve
```

This serves the real A/B/C application on loopback port 8101. It verifies actual
source bytes, opens the reserved A SQLite file, applies C migrations 1–3 and
loads 1,016 occupational references / 910 supported candidates. It uses the
committed B snapshot and source registry; there is no fixture-provider fallback.
Health: `GET /api/health`, integration mode `local_source_services`.

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
or recorded. C4.1's UI/runtime handoff and B3.1's final serving handoff were not
committed when this document was prepared; their later commits must be reviewed
and integrated before a complete application claim.

No Replit configuration/deployment was found or verified. The current user's
explicit no-deploy/no-push instruction controls release actions. Before any
later authorised deployment, the release owner must select actual hosting and
durable storage, wire the UI to this same API, verify authenticated owner
isolation and source/artifact access, configure Groq privately, and observe
worker operation. No live URL, deployed revision or competition compliance is
claimed by local tests.

## Evidence

`I2.1.json` records 147 passing ML tests, 17 distinct backend tests, compatible
versions and preserved source hashes. `I2.2.json` maps actual HTTP checks to the
required flows. `A3.1.json` records personal-service coverage, phase SHAs,
mathematical learner status and blockers. Exact local package versions and the
provider/health probe are in `I2.3.json`. No unrelated data, model weights,
credentials or SQLite files are committed or newly backed up externally.
