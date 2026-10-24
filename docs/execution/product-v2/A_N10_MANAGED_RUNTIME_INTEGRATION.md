# A-N10 — reviewed managed-Python deployment source integration

Exact missing E handoffs1905264f00e8a815d2323185a1a1987aa88cf532 and
4b53fd8d953212d009b1b928a382d9ff19ee6018 are integrated with their checkpoint
history. E owns deploy scripts/templates; A installs the root manifest/lock/config.
No E/F/D working directory or existing A runtime environment is changed.

The actual Replit configuration uses its managed .pythonlibs interpreter and
uv sync --frozen --no-dev. Root pyproject.toml is exactly E's committed template,
which preserves EVERY version and Linux CPU/non-Linux generic XGBoost marker from
deploy/requirements-hosted.lock.txt. Foundation/B training requirements and the
active provider/scorer are unchanged. No package upgrade or paid job is performed.

Root uv.lock resolves51universal entries from public PyPI with hashes, using the
existing Python3.12.15 interpreter and uv0.13.0. Exact manifest/canonical-pin
comparison PASS; Linux and Mac each select48pins with the correct mutually exclusive
XGBoost package. No NVIDIA packages are present. Linux frozen sync DRY RUN selects
48packages including xgboost-cpu3.4.1. This resolution/dry-run is not a new Linux
container execution, artifact prediction or hosted-login proof. E's earlier actual
48package Linux build remains separate; E must run the frozen build on this new
combined source, including actual provider uv-lock compatibility.

Root .replit reconciles E's reported Python3.12/PostgreSQL16/Nix25_05 settings,
vm target, single8080external service and one named Run workflow invoking the same
start script. Workflows override the default Run command; they do not start both:
https://docs.replit.com/features/workspace-tools/workflows . Configuration reference:
https://docs.replit.com/features/project-setup/configuration . TOML and shell syntax
checks PASS. Actual VM size, origin and provider behavior remain E verification;
configuration declarations do not prove those resources exist or grant upgrades.
Only generated .pythonlibs is newly ignored; raw source inputs remain visible and
untouched. pyproject.toml/uv.lock/.gitignore have one root owner, A.

E's reviewed diagnostic launcher prints only booleans/fixed codes from the SAME
process that enters the existing runtime. No credential is rewritten, returned or
persisted, no worker is duplicated and private-route checks are unchanged. Healthy
preview/worker does not imply a valid Clerk key or successful login.21combined
operator/launcher checks PASS0.247s (recheck0.221s), declared fixtures only.

Actual user-visible application evidence remains A-N9.2/A-N9.3: all three real
Qwen source-answer regressions, fresh ordinary-onboarding/one-plan/four-views/task
completion/Minder-approval/visible Explore schedule and same-revision restart pass.
227backend/136nativePostgres checks remain separate. No application/frontend source
is changed by this deployment adapter; do not regenerate or rebuild the frontend.

E's effective workflow key still contains masked-display markers after reload;
this is a credential binding/scope dependency, not a reason to bypass auth. User
has confirmed the full key saved; E is checking the actual Replit binding/scope,
not treating the stale Mac file as authoritative. Existing bucket operations and
anonymous403 passed; production DB is created through supported publishing. The
earlier automatic publish review rejection remains in force until prerequisites
are met; no publication is performed by this integration.

Next: use the exact A-N10 source SHA in A's checkpoint report, preserve Replit
configuration checkpoint9acfcd0 and4528209, integrate only committed missing changes,
run the actual frozen Linux build and same-process credential diagnostic, verify
managed auth/origin/VM and supported first-publish DB flow, then seek a new publish
review. Hosted two-user isolation/CV persistence/restart/scheduler acceptance is
still required. No main merge, force push, upgrade, secrets, DBs or model weights.
