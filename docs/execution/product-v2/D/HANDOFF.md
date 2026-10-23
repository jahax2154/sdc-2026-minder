# D3.1 — bounded state delivery and integration handoff

Status: limited overall. The implemented journey is verified; unsupported lifecycle,
extraction and content-catalogue capabilities below remain explicit. This is a local
backend delivery, not hosted/public product acceptance. No frontend or provider files
were edited. Use the commit containing this handoff as the cumulative integration ref.

| Phase | Status / delivered behavior | Verification | Checkpoint |
| --- | --- | --- | --- |
| D1.1/D1.2 | Partial profile writes; one state store; additive migration5 | 9 focused tests, fresh/repeat and disposable v4 upgrade | d887de3d7ba64541bfbb9d4ecfd3e7e73bb1b417 |
| D2.1 | Explicit direction/active plan; manual task create/edit/schedule/complete/undo/cancel; canonical progress | 14 focused tests, shared C executor records, retries/conflicts/isolation | c3906e3798e595938fb298938cf2252d458afac5 |
| D2.2 | Saved/dismissed resource state; explicit resource addition; atomic reviewed intake | 16 focused and57 backend tests | 091f9949185172b77c3b5dcad787e79748ae2b1e |
| D3.1 | WSGI error/capability checks, real-source journey and limitations handoff | Final58 backend tests; source-backed runtime and journey check | commit containing this record |

## Consumer contract

D1/D2 records contain precise input/output/transition definitions. Shared request
schemas remain A's contracts; additive ResourceToPlan/IntakeCorrection validation
is D-owned product_state_schemas.schemas(), ready for A publication. All nine
registered D product operations now advertise implemented. Profile/intake/plans
retain their existing paths. No new central routes or root dependencies were added.

E: import state_view(store, authenticated_owner) from minder_app.product_state. It
returns one read-only snapshot: profile, profile_version, direction, plans,
active_plan, progress, resource_states. Reuse its progress unchanged; filtering a
task view does not redefine progress. A null direction/active plan is a valid empty
state. Historical plans remain accessible in plans. E public-content records must
have an explicit accepted resource resolver contract before using D resource writes.
At this checkpoint only the existing two learning_options IDs are supported.

F: save a partial profile through PUT /api/profile, refetch after409; create explicit
plans with existing POST /api/plans then PUT /api/product/direction with returned
plan_id. A direction alone is valid and does not generate a plan. Task mutations
return a PlanProgress with the next state_version; refetch progress and task views.
Retry the identical request with identical key; after retry refetch, because cached
success may refer to a version older than later actions. New intent uses a new key.

C: canonical documents/history and current action services remain authority. D task
writes advance the same state_version, invalidating stale proposals as intended.
Mastery never follows activity completion. Constraints/preferences still emit C's
existing triggers, with no scheduler/provider auto-start and no implicit schedule edit.

A: ordered startup remains C migrations1–4 then D migrate(store)5 (already wired by
product_runtime.build). Only D owns new migration SQL; no mirror profile/task tables.
Update A's bootstrap-only checks before product acceptance: test_bootstrap.py's
assertion that *all* operations are unavailable describes P0.2, and is superseded
by D's tested implemented registry. It was not edited from D's lane. Reconcile
product contracts for ResourceToPlan/IntakeCorrection and E's resource resolver.

## Observed checks and runnable commands

Run from D with the existing .env.local (never print/copy its values):

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D --check
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/D/check_journey.py
```

Final unittest discovery:58 passed. Final WSGI checks cover401 unauthenticated,
200 empty progress with null fraction,422 unknown input,409 stale profile,
404 unavailable E view and sanitized {code,request_id}; all9 D capabilities
implemented. Other tests cover cross-user404, exact retries and atomic failures.

Runtime health: status ok, mode local_source_services, D8104/9104, namespace
session-d, provider_configured false; model configuration qwen/qwen3.8-27b preserved.
No TCP server was left running; no public URL/deployment. Journey script uses
actual1016-role local catalogue, selected onet:11-1011.00, a fictional profile,
disposable D-only DB and real WSGI serialization. Verified partial save -> explicit
empty plan/selection -> null empty progress -> retry-safe resource/task addition ->
completion -> new Application/Store refetch -> undo -> unchanged empty skill evidence.
Zero provider calls, no model training and no external fetches. The temporary DB is
cleaned by the script; the runtime --check initialized only the reserved D DB.

## Explicit remaining capabilities and limits

- TXT <=64KiB only; structured user review/correction is supported. No PDF/DOCX/OCR,
  automatic CV extraction, draft-list route or upload-cleanup/expiry policy.
- No demo reset or permanent account deletion operation exists in the registered
  contract. No destructive control was invented; job/proposal deletion and retention
  semantics need A/C coordination before activation. D3 lifecycle is limited.
- Existing Profile schema/scale validation and input source restrictions remain;
  global catalogue validation for all profile evidence/preferences is not added.
  Task skill/evidence/resource references are checked against available runtime IDs.
- Requirements/gaps and feasibility remain explicitly unavailable/unknown when
  source evidence, effort or capacity is absent. Direction selection is not assessed
  eligibility or readiness. Existing preparation preview remains a separate service.
- Task edit supports title/description/effort; reschedule supports time/effort. No
  dependency graph editor, arbitrary completed-task rewrite, cancellation restore,
  task deletion or skill certification capability is claimed.
- Resource writes accept existing python-tutorial/microsoft-tsql only. Additional E
  article/content IDs require the published resolver handoff. No E-owned cache or
  second user store was added.
- Local bearer sessions/plaintext permission-restricted SQLite are existing demo
  infrastructure. Production identity, hosting, encryption/retention and backups
  are unverified; this checkpoint does not claim those capabilities.

Unrelated untracked ml/minder_ml_starter/raw/ and derived/ were present at entry,
left untouched, excluded and not backed up by D. Local .env.local, runtime SQLite,
caches and source data are excluded from commits; no backup of those is claimed.
All reviewed task source/tests/reports are committed, with no history rewrite.
Only session/d-profile-state is authorized/published; no main merge or deployment.
