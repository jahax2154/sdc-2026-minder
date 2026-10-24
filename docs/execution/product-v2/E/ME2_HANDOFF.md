# ME2 — one prepared Python deployment candidate, hosted acceptance pending

E dependency chain includes M0 `719c8731ff54c73065f675267556e04d14c17a96`,
ME1 `3c32027b60b01320e4c6d4e90d12da0b66128407`, D mounted persistence
`c24c100353275dd010ea100910ea3c0a0cb07f7d`, D CV/PDF
`ab0a8f852171553074c990e80e6722e6b75af656`, and A integrated
`798b2a87437e1fd93e27cccaf9d22fa3635858e8`. Full E checkpoint SHA is supplied
with publication; do not cherry-pick wrapper files without their committed A/D
dependencies. F's final managed-login/full-page acceptance remains A's integration.

Selected single engineering target: Railway persistent-volume service, preserving
SQLite and the existing Python/vanilla app. Replit was genuinely inspected first;
its candidate career project is the old React/Express app with dev PostgreSQL,
no Python backend, managed login, production DB/private objects or hosted scheduler.
An unfinished DB conversion is the concrete Replit blocker. No second host code,
new PostgreSQL conversion, React/Express scaffold or billable provisioning performed.

E owns auth_adapter, hosted_worker, their named tests, deploy/** and these reports.
A owns all routes/middleware/HTTP CSP and the actual application factory; D owns
identity mapping, SQL/migrations/Store/private bytes/conversations; F owns login UI.
The exact implemented auth routes are GET /api/auth/config and /api/auth/session,
documented by A. No client owner or anonymous hosted fallback is accepted.

## What is prepared and verified locally

- Official Clerk7 SDK signing/origin/audience/expiry checks with generated RSA test
  JWTs, provider active-session revocation check, safe public login config. Actual
  A WSGI/D owner mapping tested with two distinct generated identities: cross-user
  profile/conversation404, restart-stable mapping, expiry/logout401 and no anonymous
  hosted bootstrap. Live provider session reads are test doubles, not real accounts.
- Existing Worker loop hosted beside concurrent HTTP on one mounted volume. A's
  actual worker persists one notice and D appends it atomically to the same Mindbot
  singleton; restart reconciliation appends saved missing notices without job replay.
  Local due-without-browser, reopen, dedup, queued pause and bounded retry tests pass.
- Python3.12 dependency install/lock (including pypdf6.21.2), explicit Python Docker
  build, one Railway config path, production env template, actual mount/identity/
  provider gates, bounded server/worker supervision and safe status-only logs.
- Data inventory/allowlisted pack/fetch for four licensed O*NET CSVs only. Fresh
  bounded official downloads match all four existing hashes. Equivalent Docker
  filesystem layout loads1016roles, real resources and canonical policy. Other
  nine raw/derived inputs, held Galaxy bulk, raw job descriptions, user DB/CVs,
  credentials, caches and weights are excluded. Attribution is retained for F.
- D backup/migrate operator commands and documented volume+CV recovery procedure;
  no automatic anonymous adoption, downgrade, overwrite or actual restore.

Observed final check at this checkpoint:129 backend tests pass in isolated
Python3.12 with the real SDK installed, plus4 deploy candidate tests. Loopback
concurrency tests required sandbox escalation and passed. Equivalent-layout smoke
passed. These are local engineering checks, not hosted acceptance or live login.

```sh
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m unittest discover -s apps/backend-api/tests
/private/tmp/minder-e-auth-py312/bin/python -m unittest deploy.test_candidate
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m deploy.verify_package
```

## A/operator next action and exact outstanding access

Use deploy/README.md and runtime.env.example. Connect the existing Railway project
with verified credits/plan/service/volume access; current Mac has no Railway CLI,
config or token and its available integration is unconnected. Confirm available
budget before using resources. Provision/reuse Clerk within its free/existing plan,
set the exact server/private/public fields in the provider secret interface, and
provide two independent test/judge accounts. Never paste credentials in chat.
Configure the existing Groq key for the published runtime, not only the Mac.

Run the actual Linux Docker build and hosted service; test health/auth/CV/private
reads, persistence across restart, backup/recovery, full F UI and a due daily check
with browsers closed. Reopen the same Mindbot conversation and verify exactly one
stored result, then pause/cancel/retry/catch-up without repeated actions. Final
cancel/next-run/scope behavior awaits D/A's committed automation extension; it is
not certified by the legacy enable/pause test. No hosted scheduler or restart proof
exists until these steps run on the real target.

Railway published-rate scenario:1GBRAM +0.25averagevCPU +0.5GBvolume is
$15.075/month, approximately$0.5025/day on30days, plus egress/backups/plan minimum.
Actual resource use, account allowance and charges remain unverified. Clerk Hobby
advertises$0 with the needed prebuilt login; no paid addons/upgrades are authorized.
Links/rates/assumptions are in deploy/README.md; this is not an approved new expense.

User already authorizes judge publication AFTER integrated acceptance and verified
cost/access within existing resources. Do not repeat generic deployment approval;
do not publish this engineering checkpoint as an accepted judge release. A provides
the accepted integrated full SHA and E coordinates that scoped publication.

Unrelated untracked raw/derived inputs remain untouched and are not backed up by
these commits. Private config/runtime DB/uploads stay uncommitted. Temporary SDK
environment and hash-checked source downloads are local checks only, not a backup.
