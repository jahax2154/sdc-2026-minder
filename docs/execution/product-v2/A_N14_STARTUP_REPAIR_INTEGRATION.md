# A-N14 — reviewed E startup repair, exact combined candidate

Integrated E c7f114221a59d766a3ee737ca4c60041ae98d4c4 through a history-preserving
fast-forward from A1df0593d31a6e1e3c97eda5ff94ff4fb37af9ee9. All intervening E
checkpoints/merges and source/template fixes are retained. The official E remote tip
was verified at c7f1142 before integration. No other worktree was edited.

The commit containing this A acceptance note is the new combined candidate; its
exact SHA is reported after commit and verified normal push. Its application source
equals the reviewed E repair. This note approves the bounded source change, not a
passing deployment. It does not authorize package/runtime upgrades or billing changes.

## Confirmed failure and bounded implementation

E's handoff records the confirmed published start.sh failure: cannot execute
.pythonlibs/bin/python, exit127. The preceding e5f0e25b build completed its final
CPU-XGBoost import. The exact published filesystem cause (absent path, broken link,
or different working directory) is not established; no such cause is invented here.

E-owned build/start scripts now anchor the repository root from their own paths.
They choose only an existing /nix/store/.../bin/python3 from PATH, require Python3.12,
and build dependencies with the same interpreter using frozen uv sync. Startup
loads the built .pythonlibs/lib/python3.12/site-packages directly with that module
interpreter. It performs no runtime installation or workspace-venv copying.

The new bootstrap checks required dependency imports originate in that built
directory and their versions match uv.lock. It checks application imports, frontend
entry files and all four pinned existing data inputs, then enters deploy.replit_launch
exactly once in the same process. The API/worker/identity/action logic is unchanged.
Missing interpreter, dependencies, imports, assets or data produce fixed safe codes.
No arbitrary system-python fallback is introduced. If the module interpreter or
dependencies are absent in the published image, it still fails honestly.

Diagnostics contain controlled filesystem/version/binding facts, not environment
values, keys, DB URLs, user data or arbitrary provider exceptions. The existing
runtime records its actual bound 0.0.0.0 port and worker liveness after bind. These
diagnostics are necessary because published shell access was unavailable.

## A verification

- 26 deployment checks PASS, 0.336s, including the five committed bootstrap checks:
  wrong Python version, missing dependency directory, exception redaction,
  check-only without launch and single existing-launcher handoff.
- 231 backend checks PASS, 13.870s, no skips; socket-enabled localhost tests included.
- bash syntax for build/start/python helpers and git diff --check PASS.
- Root pyproject.toml and uv.lock remain byte-identical to A1df0593; E's manifest
  template parses identically to root. No dependency version/OS marker/hash changes.
- This review and these fixture checks run on A's macOS check environment. They are
  not native Replit Linux, published-image or real-account browser acceptance.
- E separately reports actual workspace Nix Python3.12.12 with built-site dependency
  imports verified. That remains workspace evidence, not proof of published startup.

## E next steps and release boundary

Load the exact reported combined A commit while preserving private configuration,
database, bucket and current Reserved VM settings. Run the full native frozen build,
the bootstrap --check, and startup from a different CWD using a dependency-only test
directory with no bin/python. Verify expected import/pin/data facts and one process/
worker. Use isolated disposable paths; do not remove the existing runtime or inputs.
Only after these pass, retry the existing VM within the confirmed credit authorization
through the allowed UI path; do not bypass the connector review rejection.

Capture the new runtime's safe path/python/preflight/bound-port events and first fixed
failure if any. If public health/revision succeeds, run the real managed-user journey,
isolation, durable history/CV/plan/task, restart and due-worker acceptance. No passing
public revision or hosted journey is claimed now. Source quality and prior local
product acceptance remain separate, preserved evidence.

Untracked raw/derived inputs and private configuration, DBs, caches and bulky
artifacts remain excluded and untouched. No new backup claim is made for them.
