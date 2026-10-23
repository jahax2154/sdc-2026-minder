# Separate-clone start — local backend, no deployment

Use the **full P0.3 starting SHA in A's verified bootstrap response**, obtainable
from the published A history. Do not assume old pack references are the start.
Repository access is required. D/E/F own their branch publication; do not race
an existing owner. Existing local worktrees already provisioned by A should use
LAUNCH.md instead of repeating these steps.

```sh
git clone https://github.com/jahax2154/sdc-2026-minder.git minder-product
cd minder-product
git fetch origin session/a-personal-integration
START_SHA=FULL_VERIFIED_P03_SHA
git cat-file -e "$START_SHA^{commit}"
# D example, only if no existing assigned branch/work is being resumed
git switch -c session/d-profile-state "$START_SHA"
python3 -m venv .venv
.venv/bin/python -m pip install -r ml/requirements-foundation.txt
export MINDER_PYTHON="$PWD/.venv/bin/python"
export PYTHONPATH=ml/src:apps/backend-api
```

For E use `session/e-explore-resources` and `--lane E`; F uses
`session/f-product-frontend` and `--lane F`. If an assigned remote branch already
exists, inspect its ancestry and coordinate with its owner; do not replace it.
Python3.9+ is required. The launch on Junhong's Mac reuses its existing interpreter;
the fresh-clone install above is only for a genuinely new machine, not a rebuild.
CPU dependencies/source inference suffice; no model training or artifact download.

The clone omits13 untracked readonly source inputs. Obtain a **permitted** local
raw/derived pack whose hashes match `docs/execution/parallel/source_snapshot.v1.json`
from the source custodian. Git access alone is not permission to redistribute it.
Do not send real-user DBs/profiles/CVs or upload the input pack to GitHub.

```sh
# Run only after INPUT_PACK is a permitted local raw/derived pack root.
"$MINDER_PYTHON" docs/execution/parallel/A/checks/provision_dev_inputs.py --source-root "$INPUT_PACK"
"$MINDER_PYTHON" docs/execution/parallel/A/checks/provision_dev_inputs.py
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D --check
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane D
```

The provisioner verifies all13 SHA256 hashes before copying, refuses overwrites
and preserves readonly modes. No public download or invented fixture fallback.
Without access, record source-dependent runtime verification as blocked; continue
owned UI/schema/unit work with clearly labelled disposable test fixtures only.

D/E launchers disable external providers. F/A require authorised backend config
for real chat. Never request/copy another person's key through Git or browser code.
An authorised operator can privately provision a0600 environment file accepted by
`minder_app.config.load_provider_config`, then set `MINDER_GROQ_SECRET_FILE` to that
local path. `GROQ_MODEL=qwen/qwen3.8-27b` must preserve the verified model. Do not
commit the file or echo/source-print its contents. Missing access means real chat
is unavailable, not a reason to present mocked responses as real. The Mac's
private A config path is not available on a remote machine.

The launcher serves API and frontend `/api` on the same origin. A remote browser
cannot reach Junhong's localhost. Run this backend alongside your frontend in
your own authorised local environment. No public tunnel, hosting, deployment,
hosted authentication/storage or continuous scheduler is authorised by this pack.
Bootstrap UI503 is expected until F creates `apps/frontend-product/index.html`.

Read AGENTS, OWNERSHIP.json, CONTRACTS.md, exported C frontend contract and the lane
prompt before editing. Keep one worktree/branch per writer and one D migration
owner. Record installed dependency versions, run focused tests, review/stage only
owned paths, then commit and normally push only your assigned branch. Verify the
remote SHA and hand A an immutable full SHA with dependency/check evidence. Never
include environments, DBs, credentials, caches, weights or the13 input files.
