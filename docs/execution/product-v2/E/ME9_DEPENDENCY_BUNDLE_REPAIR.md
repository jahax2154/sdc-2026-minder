# ME9 — explicit build-library deployment artifact

Baseline approved source98073d18dd10e947327b05e9956f1d529e631bdc.
Actual controlled build7ffccaf2-2ec6-489c-9143-71ce60d7026d failed at startup.

## First fatal reported BEFORE changes

21:23:34.487Z: minder_startup_fatal code=built_dependency_directory_missing.
Location in deployed source: deploy/replit_bootstrap.py33, verify()'s required
site-directory check. User independently confirmed the exact same log line.
Exit1 followed at21:23:34.504Z. The earlier exit127 is not this attempt's error.

Actual published cwd and script root both /home/runner/workspace. Actual selected
interpreter is the Nix module Python3.12.12, outside .pythonlibs. The entire app-root
.pythonlibs path, pyvenv.cfg, bin/python and lib/python3.12/site-packages were absent.
The interpreter/CWD repair therefore reached the new bootstrap successfully.

No explicit artifact-exclusion rule was exposed by logs/metadata. Root .gitignore
contains .pythonlibs/, but that alone is not proof of the publisher's mechanism.
External/global dependency availability was not established; the proven failure is
absence of the specific app-relative dependency tree required by this launcher.

## Bounded follow-up

Build now creates a fresh task-owned temporary Python environment, with the SAME
verified Nix3.12 module and unchanged frozen uv.lock/default runtime group. It does
not copy the development environment or change dependency versions. After validating
its imports/pins/data and pip consistency, it copies ONLY built site-packages into
normal deployment output deploy/replit/runtime_packages. No interpreter, activation
scripts or pyvenv.cfg are exported; virtualenv shims/bytecode are omitted.

A generated marker records the lock digest, format and Python version. Rebuild
replaces only an output bearing that marker; unknown destinations and symlinks
are rejected. The generated nested ignore exception retains public wheel data
such as certificate PEMs even if source-secret ignore patterns are consulted.
Runtime checks the bundle marker against the deployed lock and checks import origins
and version pins, then uses the unchanged API/single-worker launcher. No download,
resolution, installation, unpacking, DB/schema/auth/scoring or frontend change occurs
at startup. Secret-free path/version diagnostics include the new artifact directory.

## Source/checkpoint boundaries

Generated runtime_packages is NOT source and MUST NOT enter any Git checkpoint.
Run validation builds in an isolated temporary checkout. Load only the approved
source into main; do not generate this output there before Agent auto-checkpoints.
The controlled publishing BUILD generates the deployment artifact in its build
container. Do not add a source ignore rule that might suppress this required
artifact. Stage explicit source/document/test paths only. No bulky dependency output
was generated or committed in E's worktree by this repair.

25 focused checks pass, including bundle copy/public certificate data, recognized
output rebuild, unknown-destination preservation, deployed-lock mismatch rejection,
wrong Python, missing dependency output and existing launcher/check-only boundaries.
Shell syntax and diff checks pass. Native fresh build and copied-bundle startup from
another CWD with NO .pythonlibs remain required before the next controlled publish.
Public health/login/data/restart/worker acceptance remain unverified.

Preserve existing Reserved VM, database, bucket, Clerk Development instance, server
Secrets, API/worker behavior and existing-credit-only authorization. First new fatal
must again be reported before any further source/config change or publication.
