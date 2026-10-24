# A-N15 — explicit build-library output integration

Exact E handoff: 03fcbc28e8e0627373cd783052968142fd5b358a, verified on the official
session/e-explore-resources remote and fast-forwarded into A from98073d1. All prior
checkpoints remain intact. The commit containing this note is the new combined
candidate; its immutable SHA is reported after commit and verified normal push.

## Actual failure and preserved boundaries

E/user confirmed build7ffccaf2-2ec6-489c-9143-71ce60d7026d's first startup fatal:
built_dependency_directory_missing at21:23:34.487Z, exit1 at21:23:34.504Z.
The actual published cwd and script root were /home/runner/workspace, and the
selected module Python3.12.12 ran. The .pythonlibs directory and its bin/lib/cfg
paths were absent. Thus the interpreter/root repair reached its intended diagnostic;
this attempt's cause is not the preceding exit127. The platform's precise artifact
exclusion mechanism remains unproved. No claim that all global dependencies were
absent is made.

E's committed build-only repair uses a fresh disposable environment with the same
Nix module interpreter and unchanged frozen lock/default runtime group. It verifies
the installed imports/pins and copies only the built site-packages libraries into
deploy/replit/runtime_packages. It does not export a venv, interpreter, activation
scripts or pyvenv.cfg. Virtualenv shims/bytecode are omitted. A marker binds the output
to uv.lock's SHA256. Only an output bearing the recognized generated marker can be
replaced; unknown destinations and symlinks are rejected. Temporary build cleanup
targets only the fresh mktemp directory.

Startup uses that explicit non-hidden build output, verifies its marker, import
origins, exact pins, source data and assets, then enters the existing single-process
API/worker launcher. No runtime installation, extraction, download, auth bypass,
provider/model/scoring change, DB migration or frontend change. The scoped generated
ignore exception preserves public wheel data such as certifi PEMs in the artifact;
it is not a source ignore rule or permission to commit third-party libraries.

## A checks actually run

- 29 deployment checks PASS, 0.288s. These include copy/rebuild of recognized output,
  preservation of unknown destinations, retention of public certificate data despite
  source ignore rules, lock mismatch rejection and prior bootstrap/launcher guards.
- bash syntax for build/start/module helpers and git diff --check PASS.
- Root pyproject.toml and uv.lock are byte-identical to98073d1. Reviewed seven incoming
  E source/test/evidence paths contain no credential-shaped values or bulky artifacts.
- deploy/replit/runtime_packages does not exist in A's checkout. No build was run in
  this source worktree, and raw/derived/private environments/DBs remain untouched.
- These are local controlled checks, not a published image test. The previous
  231 backend checks at A-N14 remain separate; no backend business source changed.

## Exact E next handoff

Run the actual fresh frozen Linux build in an isolated temporary source checkout.
Test a real COPY of the generated library bundle in an independent layout, with no
.pythonlibs directory and a different CWD; require strict pins/import origins/assets/
data checks to pass using Nix Python3.12.12. A linked build-site fixture alone does
not prove this copied output. Keep generated dependency output outside Git and
provider source auto-checkpoints.

Load only the exact approved combined source into the actual Minder provider root,
preserving private configuration/resources. The controlled publisher's BUILD must
generate runtime_packages in its build container; do not run a full build in the
provider source root before automatic source checkpoints. Then retry the existing
Reserved VM only after native copied-output checks pass, within existing-credit
authorization and the allowed UI path. Retain the first safe fatal/bind evidence
before making any further repair.

Public health/revision, managed login and all hosted user/isolation/durability/worker
journeys remain unverified. The failed deployment history is not reclassified as
successful. No deployment is initiated by this A integration. Excluded local state
has no new backup claim.
