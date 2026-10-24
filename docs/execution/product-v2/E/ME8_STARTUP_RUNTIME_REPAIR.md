# ME8 — focused Python startup repair

Target: existing Minder0f48cf79-f55a-4b24-ba5c-a03d800e03bd, existing Reserved VM.
Preserved baseline: E24a5c52579009ae2c5a3b7390e36f8b6121327ad, containing A1df0593.
No completed product phase, authentication tenant, DB schema or feature is restarted.

## Evidence boundaries

- Workspace .replit: build bash deploy/replit/build.sh, run bash deploy/replit/start.sh,
  modules Python3.12/PostgreSQL16, configured local8080/external80. Effective published
  dashboard overrides and actual runtime port are not exposed by connected metadata.
- Actual build e5f0e25b: final CPU-compatible XGBoost import marker exists; the old build
  successfully executed .pythonlibs/bin/python. No published filesystem proof follows.
- Actual published runtime: supplied/confirmed start.sh error cannot execute
  .pythonlibs/bin/python, exit127. Missing directory versus broken link versus CWD
  mismatch is not yet established. Effective CWD, published symlink target and published
  Python/dependency filesystem cannot be inspected through connected shell access.
- Workspace .pythonlibs IS a venv: pyvenv.cfg exists, bin/python is executable and its
  target exists. The base executable is Nix python-wrapped outside .pythonlibs, Python
  3.12.12. That base interpreter with .pythonlibs/lib/python3.12/site-packages imports
  jwt, Clerk, psycopg, private App Storage, NumPy/SciPy/sklearn and CPU XGBoost3.4.1.
  This is workspace evidence, not a claim about the failed published runtime.

## Bounded repair

Build/start anchor CWD and PYTHONPATH to script-derived repository root. Both select
only the existing Replit/Nix Python3 module outside .pythonlibs; there is no venv,
/repl/tools or arbitrary system-python fallback. Build passes that exact interpreter
to frozen uv sync. Version guard requires3.12. Dependencies are still built during
build, not installed during startup. No dev environment is copied into a deployment.

Startup consumes the built Python3.12 site-packages directory directly and verifies
required imports originate there with versions matching uv.lock. It verifies actual
application imports, frontend entry files and all four existing pinned runtime data
inputs before entering the unchanged deploy.replit_launch in the same process. No
API/service/worker behavior changes; no extra scheduler or provider/database probe
is created by the check-only mode. Runtime logs binding0.0.0.0 and actual validated
port after binding and starting the existing single worker.

Secret-free shell prelude records selected CWD/root/interpreter, old interpreter path
existence/executable/symlink facts and link target. Python prelude records version/base
prefix and fixed fatal import/pin/asset/data error codes; no environment, credentials,
connection strings or arbitrary exception payloads. If the published module interpreter
or built dependency directory is absent, startup fails specifically rather than trying
another interpreter or downloading dependencies. This next controlled deployment is
also the required actual-runtime diagnostic because production shell access is absent.

## Checks and remaining proof

22 focused startup/launcher/runtime/operator tests pass; shell syntax and diff checks
pass. Tests cover wrong module version, absent packaged dependencies, exception
redaction, check-only no-launch and exactly-once existing-launcher handoff. Native
Replit full build and launch from a different CWD with a dependency-only directory
(no bin/python) remain required before publication. Published runtime availability,
working public health/revision, real login/chat and remaining hosted journeys are
NOT yet verified. A must receive exact E SHA and approve the combined deploy pin.

Database, existing private bucket, Clerk/Groq Secrets, provider, dependency versions,
scoring and frontend design remain unchanged. Existing allowance only; no purchases,
top-ups, migration or authentication bypass. Untracked inputs/private configuration
remain excluded; no backup claim is made for excluded local state.
