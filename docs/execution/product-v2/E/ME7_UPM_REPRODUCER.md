# ME7 — actual Replit UPM parser failure

Correct Minder project: 0f48cf79-f55a-4b24-ba5c-a03d800e03bd.
Second actual Reserved VM build9dd5d9fd-4065-4ffe-a1c9-4ebaf61c0e96 failed with
UPM nil-pointer SIGSEGV at python.go848, makePythonUvBackend.func1, reached from
func11 at1108. Logs show Installing packages and Resolved51; explicit project
build execution was not established. The earlier documented enabledForHosting=false
setting did not prevent this deployment from running UPM. Public health/auth404;
no deployed runtime or hosted acceptance success is claimed.

## Actual isolated provider check

Replit reports installed UPM0.0.0-0ffdf7d. Read-only command:
`upm -l python list -f json`. Each case ran in a separate temporary directory,
with a PATH-only subprocess environment. No project root, credentials, runtime DB,
package installation/resolution or publication was changed by these checks.

| Input metadata | Exit | Result |
| --- | --- | --- |
| Two plain pinned XGBoost dependencies | 0 | Two dependencies listed |
| Same pair with current PEP508 platform markers | 2 | Same nil-pointer SIGSEGV at python.go848 |
| One plain control dependency | 0 | One dependency listed |
| Plain project dependency; marked pair in default runtime group | 0 | Project dependency listed, no panic |

The [official UPM parser](https://github.com/replit/upm/blob/main/internal/backends/python/requirements.go)
anchors its supported package/version expression without environment-marker syntax.
The [UV project parser](https://github.com/replit/upm/blob/main/internal/backends/python/python.go)
dereferences the missing parsed package name at the observed failure line. These
source observations now agree with the installed provider binary's controlled test.

## Bounded repair and proof limits

A owns root pyproject.toml/uv.lock. Move only the two existing marked XGBoost entries
into a default uv runtime dependency group; preserve both pins and OS conditions.
E mirrors that configuration in deploy/replit/pyproject.toml. Parsing and set equality
checks show the template retains exactly the same dependency strings and selects
runtime by default, with no marked strings left in project.dependencies.

[uv documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#default-groups)
documents default groups; --no-dev excludes dev, not the named runtime group.
No application, auth, DB schema, storage, model, scoring, package-version or billing
change. Preserve Linux xgboost-cpu3.4.1 and other-platform generic xgboost3.4.1.

The isolated metadata check does not prove frozen installation or publishing.
Before any next publication, load A's exact approved group-repair pin, run installed
UPM listing against the full actual manifest, then the existing frozen build/start,
Clerk match and worker checks. Preserve provider configuration and user Secrets.
Only the existing VM UI path is authorized for retry; connector retry review rejected
uncertain VM retention after a failed first publish. No indirect bypass occurred.

## Approved full-application verification

A approved source1df0593d31a6e1e3c97eda5ff94ff4fb37af9ee9; handoff is
../A_N13_R01_UPM_MARKER_COMPATIBILITY.md. Replit loaded it preserving configuration
at actual Git HEAD7cc7f2d9a5a3943ba20c31a4c1845359514b0979.

Actual FULL ROOT native UPM listing exits0,47dependencies,no panic. Frozen Linux
build passes with48installed distributions and dependency checks. CPU XGBoost3.4.1
imports; non-Linux distribution is absent. Preview health200 reports the exact new
source pin, same-process live Clerk match is true, one launcher and its existing
cohosted worker run. E template parses identically to approved root semantics.

These prepublication checks now pass against the actual imported implementation.
A further public VM build and hosted user/restart/delivery acceptance are still
required; no successful deployment SHA is claimed here.
