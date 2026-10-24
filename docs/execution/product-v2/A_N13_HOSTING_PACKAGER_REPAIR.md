# A-N13 — bypass crashing automatic hosting installer

Parent: 74b9688e124f0e6d5f2eb57943fd2671614dab9a. The commit containing this
handoff is the approved combined candidate on session/a-personal-integration;
the coordinator reports its exact SHA after committing and remote verification.

## Evidence and repair

E reports that the first actual Reserved VM publication failed before the explicit
project build. Deployment ID: f2e97f0f-a92b-44eb-aa1f-69199e77c391. The public health
endpoint returned 404. Publishing UI logs identify the automatic Python installer:
panic, invalid memory address/nil pointer, SIGSEGV, with frames at
github.com/replit/upm/internal/backends/python/python.go:848 and
makePythonUvBackend.func11. This log is E's observed platform failure, not a locally
reproduced application error. The preceding preview frozen build was healthy.

Replit's [official packager configuration](https://docs.replit.com/features/project-setup/configuration)
documents packager.features.enabledForHosting=false to skip the automatic hosting
package installation. A adds exactly that setting to the root .replit. E owns the
deploy/replit/replit.toml template and can mirror this committed setting there.
No other lane's worktree or owned source is modified.

The existing explicit deployment build still runs deploy/replit/build.sh:
Python 3.12 guard, UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --frozen --no-dev,
approved artifact fetch, dependency consistency check and XGBoost import check.
The committed uv.lock and dependency versions are unchanged. This avoids the
redundant platform installer while preserving the actual frozen build and checks.

## Verification and handoff

- Python 3.12 tomllib parses the changed configuration. Removing only the new
  packager table yields an object exactly equal to parent74b9688's configuration.
- Reserved VM target, build/start commands, ports and workflow are unchanged.
  The explicit frozen install, artifact fetch and import checks remain present.
- bash -n deploy/replit/build.sh deploy/replit/start.sh and git diff --check PASS.
- Existing deploy checks PASS: 21 tests in 0.249s using the locked local check
  environment. These are local controlled checks, not a native publication test.
- No changes to model/search/scoring, auth/action controls, storage, DB schema,
  machine size, provider secrets, subscription or billing configuration.

E should load the exact reported new A commit with its private provider configuration
preserved, verify that automatic UPM installation is skipped and the explicit frozen
build executes, then retry the same quoted Reserved VM within the user's existing-
credit authorization. A has not initiated publication or claimed a passing deployment.
If another stage fails, retain its exact first error and repair that bounded cause.
Public health, real account login/isolation and durable journeys remain E acceptance.

Untracked raw/derived inputs, private environments, DBs and artifacts remain excluded
and untouched. This checkpoint makes no new backup claim for excluded local state.
