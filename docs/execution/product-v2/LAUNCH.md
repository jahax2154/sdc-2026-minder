# Product lanes — P0.3 launch

Ready to release D/E/F after the P0.3 commit is fast-forwarded into their still-clean
branches and its A snapshot is verified on origin. Use the final full starting SHA
from A's bootstrap response; a commit cannot contain its own hash. No reset/rebase.

## Immutable dependencies

- Verified integrated base: `07f60a8e0b3097685f99d0bc68d05edd29021391`.
- P0.1 inventory/design/pack: `bc5161bd2f43e747654e37408c56758faeb52d23`.
- P0.2 contracts/runtime: `ad1c17e78370cb81fdfcfcb2c6285dfe59451d24`.
- Included B final: `d9ffd4f3cc7625c736ea081c52da3c1122b21c08`.
- Included C final: `362316351ebe90b31c533eb75cff46a851808314`.
- D/E/F were absent, then created at P0.2. Final P0.3 is their launch base.
  No pre-existing lane work was replaced. Original checkout and B/C remain untouched.

| Lane | Absolute working directory | Branch | API / UI | Prompt in committed pack |
| --- | --- | --- | --- | --- |
| A | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-a | session/a-personal-integration | 8111 / 9111 | 02_A_BOOTSTRAP.md |
| D | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-d | session/d-profile-state | 8104 / 9104 | 03_D_STATE_BACKEND.md |
| E | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-e | session/e-explore-resources | 8105 / 9105 | 04_E_EXPLORE_AND_RESOURCES.md |
| F | /Users/phuahjunhong/sdc-2026-minder-worktrees/session-f | session/f-product-frontend | 8106 / 9106 | 05_F_PRODUCT_FRONTEND.md |

Full prompt root: `docs/Minder_Profile_Explore_Parallel_Execution_Pack_v1/`.
Use file11 launch prompts plus the addenda in `docs/Minder_Three_Hour_Prototype_Launch.md`.
Read local AGENTS and [OWNERSHIP.json](OWNERSHIP.json) before edits. Its exact
allowed/forbidden paths are authoritative; the summary below is not broader permission.

| Owner | Allowed implementation | Exclusive boundaries |
| --- | --- | --- |
| D | product_state.py, product_migrations.py, product_state_schemas.py, profiles.py, plans.py; their named tests; docs/product-v2/D | Sole new migrations starting5; preserve C migrations1–4/action authority |
| E | product_views.py, product_content.py, product_view_schemas.py; data/product-resources.v1.json; named tests; docs/product-v2/E | Reads/adapters/resources; no migrations, SQL writer or scorer |
| F | apps/frontend-product/**; docs/execution/product-v2/F/** | Sole shell/client/router/styles/package writer; preserve approved design |
| A | Central api.py/product_routes.py, shared contracts, runtime, root dependencies, integration | No concurrent writes in producer modules |

Backend relative module root is `apps/backend-api/minder_app/`; tests root is
`apps/backend-api/tests/`. D/E/F docs root above means `docs/execution/product-v2/`.
G is inactive: no worktree, branch or allowed files. Only activate after a committed
F0.2 stable client/components handoff and A/F assign exact exclusive page files.

## Isolated runtime and actual commands

Each new lane has a private ignored0600 `.env.local`, no copied credential or DB.
It points to the existing Python3.9 environment read-only. Source imports resolve
the current worktree. Do not recreate that environment or rerun closure/setup.

```sh
# D — start only in this worktree
cd /Users/phuahjunhong/sdc-2026-minder-worktrees/session-d
source .env.local
"$MINDER_PYTHON" docs/execution/parallel/A/checks/provision_dev_inputs.py
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D --check
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D
```

```sh
# E
cd /Users/phuahjunhong/sdc-2026-minder-worktrees/session-e
source .env.local
"$MINDER_PYTHON" docs/execution/parallel/A/checks/provision_dev_inputs.py
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane E --check
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane E
```

```sh
# F — actual backend on8106 and same-origin frontend/API on9106
cd /Users/phuahjunhong/sdc-2026-minder-worktrees/session-f
source .env.local
"$MINDER_PYTHON" docs/execution/parallel/A/checks/provision_dev_inputs.py
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane F --check
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane F
```

All DB/output/upload/log/worker reservations are fully listed in OWNERSHIP.json.
DBs resolve under each absolute worktree's `ml/artifacts/session-{d,e,f}/product/runtime.sqlite3`.
Generated output, uploads and logs stay under that same lane's product directory;
worker state uses that DB. No scheduler auto-starts. Do not use another lane's DB.
A product command is the same module `--lane A` from A with `source .env.local` and
`PYTHONPATH=ml/src:apps/backend-api`; runtime reserves8111/9111 independent of old
environment port variables. Existing A closure8101/9101, B8102/9102 and C8103/9103
remain reserved. Do not stop those services to run these commands.

F's server privately reads the already-authorised owner-only A provider config;
no key was copied. Exact preserved model is **qwen/qwen3.8-27b**. D/E deliberately
disable provider calls while retaining real catalogue/scoring/source services.
Never put provider credentials or session bearer tokens in committed/browser code.
This bootstrap reuses prior AC4 real-provider evidence; it makes zero new Groq calls.

With the server stopped, baseline tests in any lane:

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/test_bootstrap.py
```

Run each producer's focused new tests before handoff. `checks/verify_launch.py
--root ABSOLUTE_DIRECTORY --lane D` (or E/F) checks bootstrap TCP/auth behavior only
while no server is running. Its503 expectation is intentionally bootstrap-specific;
F's actual UI acceptance replaces that expectation once the product root exists.

## Contracts, designs and first useful slices

Read [CONTRACTS.md](CONTRACTS.md), machine schema and validated examples here,
plus `docs/execution/product/llm/FRONTEND_CONTRACT.md` and its exported envelope.
`contracts/parallel-services.v1.schema.json` remains the canonical domain schema.
A registry discovers D/E modules only when they export implemented `OPERATIONS`
tuples and `dispatch(app,owner,method,path,body)`. Planned routes return explicit
unavailable errors, never mock success. D's first state helper signature and E's
view envelope additions arrive through committed handoffs, not active-file copying.

F uses the41 approved HTML/assets/reference files at `docs/minder-ui-html-previews/`
as visual authority. Port them into its owned product root. Replace fictional
replies/schedules/user/scores/localStorage identity with actual APIs; no redesign,
framework migration or missing-DESIGN_CONTEXT gate. Product UI is not implemented
at bootstrap; existing `apps/frontend-web` is the separate acceptance UI.

- D: profile slice early, then persistent direction/task/progress using existing state.
- E: existing Explore reads early, then small real-source resource view. No crawler.
- F: shell/client plus real chat/source and exact proposal/action flow first;
  then Profile/Explore from D/E. Do not wait for all pages before the first commit.
- A: inspect full dependency SHAs and integrate useful committed slices as they
  arrive; publish compatible small contracts promptly. No duplicate history merges.

## Publication and time budget

Verified origin is `https://github.com/jahax2154/sdc-2026-minder.git`.
A publishes only its integration branch. D/E/F publish their own assigned branch;
A does not create their remote tips. All bootstrap objects are reachable through
the published A starting snapshot, so a teammate can branch from that full SHA.
Every handoff includes full SHA/dependencies, changed owned files, actual checks,
remaining gaps and next consumer action. Normal pushes only, verify remote SHA.
No squash/amend, force push, main merge, tags, PR or deployment.

Fixed budget: feature freeze **2026-10-23 17:35:23UTC / 24Oct01:35:23MYT**;
completion **18:25:23UTC / 24Oct02:25:23MYT**. Reserve the final50minutes for combined
acceptance, bounded blocking repairs and handoff; final15minutes for smoke/SHAs/run
instructions. See DECISIONS for the conservative timing anchor. Stop broad data
search, model tuning and new framework work. Unavailable dependencies do not block
independent slices. No paid jobs or deployment are part of this launch.

Local readiness is separate from real forecast accuracy, independent suitability
labels, RunPod execution proof and hosting. Localhost is not a remote teammate's
backend; see [TEAM_START.md](TEAM_START.md) for a permitted local clone setup.
