# ME6 managed Python provider configuration — A root integration required

Actual correct Replit project loaded A27bc76094ae3cbdb29d12e14c001549850593d55.
The provider's working configuration uses `.pythonlibs` and `uv sync --frozen`,
rather than creating a pip-seeded .venv inside its managed Nix Python runtime.
Build/start source was retrieved exactly as base64; plain-text markdown had removed
underscores from __version__, so that formatted diff was not blindly copied.

E exports:
- deploy/replit/build.sh: Python3.12 guard, locked managed-environment uv sync,
  existing four-artifact fetch, dependency check, actual XGBoost3.4.1 import.
- deploy/replit/start.sh: same existing app through deploy.replit_launch in the
  managed interpreter, not a new app/server/scheduler.
- deploy/replit_launch.py: in-process credential diagnostics, safe booleans/fixed
  codes only, then unchanged replit_runtime. No credential rewrite/persistence,
  auth bypass, duplicate process or private exception dump. A failed diagnostic
  does not claim login ready and does not weaken existing private-route checks.
- deploy/test_replit_launch.py: five focused diagnostic/no-leakage/runtime boundary
  checks. Combined21operator/runtime tests pass; no real provider identity claimed.
- deploy/replit/pyproject.toml: root manifest template generated from the canonical
  hosted lock, including Linux CPU/non-Linux generic XGBoost markers approved by A.
  Actual provider manifest used unconditional CPU; the template preserves A policy.

A owns installing the template as root pyproject.toml and generating root uv.lock.
These files are required before a fresh uv-based build; do not publish this E slice
alone without A's integrated root dependency commit and exact revised source pin.
An isolated uv lock resolution of the template succeeds with51universal packages
(including root/alternative-platform entries) and no NVIDIA packages; actual Linux
provider build selected48packages and passed before this source handoff. Mac/CI
resolution is not relabelled as a published Linux container or prediction proof.

A also owns root .replit/replit.nix/ignore decisions. Review the actual provider
configuration: Python3.12 + PostgreSQL16 modules, vm target, Nix stable25_05 packages,
Run button with one Minder runtime workflow waiting on8080. Preserve provider
checkpoint4528209 and current local configuration HEAD9acfcd0. Do not blindly copy
unrelated agent expertMode or broad raw-input Git ignore changes. Environments,
credentials, DBs, model weights and caches stay out of commits. Build packages only
four approved existing public inputs; verify final published data packaging.

The private user bucket has real put/get/delete/deletion probes PASS; anonymous
access403. Managed preview health200 at27bc and one worker alive. Production DB is
created during first publish per official Replit workflow, not directly by Agent.
No published judge URL/SHA or managed-user/restart/scheduled-event proof exists.

Current blocker remains runtime CLERK_SECRET_KEY non-ASCII after workflow reload.
User confirmed full-key entry; shared/inherited binding presence is reported but
scope versions unavailable. No plaintext/inline override or duplicate name found.
Exact scope clarification is pending; no secret has been printed or guessed.
Automatic publication review rejected the earlier attempt due unverified auth/
startup/VM/origin and default Autoscale; publication stays paused, no bypass.
