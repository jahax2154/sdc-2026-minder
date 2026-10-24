# A-N13-R01 — preserve runtime pins outside UPM's broken marker parser

Parent: 5689d46f3884cc69a441d551450075862d4ad292. This is a bounded refinement of
A-N13, whose history and evidence remain intact. The commit containing this file
is the candidate pin for E's isolated provider verification; its exact SHA is
reported after normal push. Do not retry publication solely on local evidence.

## New actual failure and cause

E observed retry build9dd5d9fd-4065-4ffe-a1c9-4ebaf61c0e96 fail in the same UPM
automatic package-install stage, before the explicit build command. Therefore the
documented enabledForHosting=false switch did not prevent UPM from running in this
actual publishing path. It is retained, but is not claimed as a successful fix.

The first error is again a nil pointer in python.go:848 (makePythonUvBackend
listUvSpecfile), called by the install path around1108. The inspected public
[Replit UPM parser](https://github.com/replit/upm/blob/main/internal/backends/python/python.go)
loops only over project.dependencies, applies MatchPackageAndSpec, and dereferences
name even if no match occurred. Its
[requirements parser](https://github.com/replit/upm/blob/main/internal/backends/python/requirements.go)
anchors name/extras/version syntax without PEP508 marker support. Our two valid
platform-marked XGBoost requirements fail that expression. This source inspection
explains the observed panic; it is not yet execution of Replit's installed binary.

Local source copies inspected under /private/tmp/minder-a-upm-parser have SHA256:

- python.go: 0ac96f7159dc88405fdde85bdd1f6b5bed5930ddf156bf60ace7f6343cbb284e
- requirements.go: 1c9111e579734ae9f4623221a5e32413657540812f3dc554f809534619208cbb

## Exact bounded change

Move only the two unchanged marked strings from project.dependencies into
dependency-groups.runtime. Set tool.uv.default-groups=["runtime"]. The project is
already a virtual runtime environment, not a published Python library. The default
group is included by both UPM's uv sync and our uv sync --frozen --no-dev. The latter
excludes only the dev group, not runtime. This behavior is documented by
[uv default dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/#default-groups).

Regenerate uv.lock offline using the existing uv0.13.0 and Python3.12.15, with no
upgrade flags. Every non-root lock record, version, artifact URL and hash remains
identical. Only the virtual root dependency grouping metadata changes. Linux still
receives xgboost-cpu3.4.1; non-Linux receives xgboost3.4.1. No NVIDIA dependencies.
E alone can mirror this layout in its owned deploy/replit/pyproject.toml template.

## Verification actually run

- All49 original requirement strings exactly equal project.dependencies plus the
  default runtime group; no pin/marker additions, removals or changes.
- All50 non-root lock records deeply equal the parent;51 universal records remain.
- Transcription of the inspected upstream regex rejects exactly the two former
  project entries, and accepts every new project entry. This is a local parser
  compatibility probe, not a native UPM execution. No Go toolchain was installed.
- E separately reports an actual installed-provider reproduction using UPM
  0.0.0-0ffdf7d, command upm -l python list -f json, isolated temporary directories
  and a PATH-only environment: plain two-pin control exits0/count2; the same pair
  with the original PEP508 markers exits2 with the exact python.go:848 nil-pointer
  panic; a plain one-pin project plus the marked pair in the default runtime group
  exits0/project-count1 without panic. No installs, resolution or provider root
  writes occurred. This native minimal reproduction is E-reported evidence; the
  new full committed manifest still needs the same actual-provider check.
- uv lock --offline and uv lock --check --offline PASS with the existing Python.
- Frozen no-dev sync DRY RUN PASS for Linux x86_64 and the local macOS platform:
  each selects48 packages, with the correct mutually exclusive XGBoost distribution.
  No actual environment is installed or modified by these dry runs.
- git diff --check PASS. Root pyproject.toml and uv.lock are A-owned. Build/start,
  authentication, source retrieval, model/scorer, action authority, DBs and private
  configuration are untouched. Prior backend and browser results are not rerun or
  relabelled as hosted proof for this manifest-only change.

## E handoff and next check

Load this exact committed manifest/lock into an isolated non-production provider
directory first. Use Replit's actual installed UPM to reproduce the old marker
failure and show the new manifest avoids it. Record the binary/version, command and
outcome. Then run the actual frozen Linux build and dependency/import checks and
verify the candidate remains healthy with the existing private provider settings.
Only then retry the same Reserved VM within the existing-credit authorization.
No environment upgrade, package upgrade, alternative deployment type or billing
change is authorized by this repair. If UPM rewrites the lock, compare all pins and
artifact hashes and report any changes rather than silently widening the scope.

Actual public deployment and managed-login/journey acceptance remain pending.
The first two failed publication attempts are preserved, not replaced with passes.
Raw/derived inputs, private environments/databases and bulky artifacts remain
excluded and untouched; no new backup claim is made for that local state.
