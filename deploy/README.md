# Minder Python deployment candidate — Railway only

Revision3 section4 selection: Replit was inspected first. Existing shared project
Aiversecity Career Compass is React/TypeScript/Vite + Node24/Express, with no Python
app, managed auth, production DB, private storage or worker. Only development
PostgreSQL16.10 exists; profile is browser session storage. Replit source inspection
confirmed these facts read-only. The actual SQLite app needs a new PostgreSQL
conversion there, a concrete blocker. Do not upload the old mockup as Minder.

Selected engineering candidate: one Railway service, one persistent volume, existing
Python app + vanilla frontend + cohosted existing worker, managed Clerk login.
No second host implementation, PostgreSQL conversion, independent cron, new queue,
React/Express scaffold or custom passwords. Single-volume service cannot use replicas;
expect a short restart/redeploy outage. Provider documentation:
https://docs.railway.com/volumes/reference

**Account-dependent, not yet a verified hosted deployment.** No Railway CLI/config/
token was found; the available Railway integration is not yet connected. Existing
project/plan/credits and permission to attach its existing resources must be verified.
User was asked for the intended project/available budget, without requesting secrets.
No new plan, upgrade, service provisioning or billable deployment has been performed.

## Build and start

Use the accepted integrated A release commit containing the E/D/F checkpoints.
Do not deploy an E-only old UI or modify another branch. Select repository root
as source root; configure custom config path `/deploy/railway.json` in Railway.
The explicit Dockerfile is necessary to select Python in this mixed repository
rather than autodetect the legacy Node application. It uses Python3.12 slim,
libgomp1 for existing XGBoost imports, reviewed Python dependencies and the actual
frontend/API. Existing ML models are not trained at startup.

```sh
docker build -f deploy/Dockerfile -t minder-candidate .
# The provider starts this automatically, using its attached volume and variables:
python -m deploy.runtime
```

No Docker engine is available on the current Mac; an actual Linux container build
is still pending. E tested the equivalent source layout and Python3.12 dependencies
locally, not a fictional Docker/hosting result. The wrapper listens on0.0.0.0:$PORT,
uses A's existing bounded ProductServer/web_app, and refuses to start without an
actual mounted volume, production auth/provider settings, A identity boundary,
D volume-aware Store and A's persisted Mindbot Worker. Health is `/api/health`.
Dependency versions are locked from E's isolated successful Python3.12 environment.
Validate the Linux wheels/container on the real provider before acceptance.

## Configure once

1. Confirm the intended EXISTING Railway project/account, current credits/plan,
   service/resource permission and remaining cost allowance. Connect its account
   integration or use its existing authorized dashboard. No upgrade/top-up.
2. Attach one existing/permitted persistent volume at `/data` to the same service.
   One replica, sleeping/serverless behavior disabled for the always-running worker.
   Do not point a separate cron service at the same SQLite path.
3. Enter exact names from runtime.env.example in the provider's secret interface.
   Provider supplies PORT and RAILWAY_VOLUME_MOUNT_PATH. MINDER_DATA_ROOT=/data;
   DB=/data/minder/runtime.sqlite3; CVs=/data/minder/documents; document mode
   private-volume. D validates the actual mount on each connection/operation.
4. Provision the chosen Clerk application within its existing/free allowance.
   Configure exact issuer, signing public key, server secret and public key for
   the SAME instance; allow only actual hosted HTTPS origin. Use managed prebuilt
   sign-in/sign-up/logout with the current frontend, no new backend. Provision
   two independent test/judge accounts. See E/AUTH_HANDOFF.md and A's live
   /api/auth/config and /api/auth/session contract. Keep dev/live instances distinct.
5. Configure Groq in the PUBLISHED runtime: existing authorized key, preserved
   qwen/qwen3.8-27b model and daily cap. No local Mac file is required. Never put
   keys in frontend, Git, public config or logs.
6. Confirm F's CSP/login/source-attribution integration and A/D/F acceptance before
   the requested judge publication. Use provider subdomain; no custom domain needed.

## Data and migrations

Build-time provisioner fetches EXACTLY four already-selected O*NET31 CSV URLs from
official allowlisted HTTPS hosts, no other targets or private input. A bounded
fresh retrieval of all four was performed: all hashes equal the existing manifest.
Source bytes remain read-only; CC BY4 attribution/changes are in ATTRIBUTION.md.
Only those four inputs are needed for the current1016-role runtime; E's equivalent
layout test verified catalogue, real resources and canonical policy. The other nine
untracked inputs are not shipped. Held Galaxy data, raw employer job descriptions,
weights, local SQLite/user profiles/CVs/credentials/caches are not in the build.
Tracked public source snapshots/registries and policy reference files keep their
hashes, dates, scope and unavailable forecasts. Static server exposes only the
frontend root, never data directories. No new market formula or feed acquisition.

An offline input pack can be created without new downloads:

```sh
python -m deploy.artifacts pack --output /private/tmp/minder-runtime-inputs.tar.gz
```

Do not commit that artifact. Build fetch fails safely if official bytes change or
are unavailable; do not silently replace the pinned version. Supply the checked
offline pack through the provider's private build mechanism only if required.

A factory runs existing Store, C migrations and D's sole additive migration chain.
D migration7 introduces real-user mapping/conversations without giving old anonymous
records to new accounts. Start an empty hosted dataset unless an explicit verified
mapping/migration is approved. No automatic copying of Mac databases/CVs.

Before a schema-changing release, use D Store.backup(new_absolute_path) for an
online SQLite snapshot, and the provider volume backup for a consistent recovery
point including private CV bytes. SQLite backups alone do not contain CV objects;
do not copy only a live main SQLite file while omitting WAL. D backup creates a
new0600 file without overwriting existing backup. Configure provider backup retention
only within authorized resources; actual schedule/access remains unverified.

```sh
# In the selected service's private operator shell, before a release:
python -m deploy.maintenance backup --output /data/backups/pre-release-UNIQUE.sqlite3
# D's actual additive chain, no worker/model call (also runs at startup):
python -m deploy.maintenance migrate
```

Recovery: stop the single web/worker service, preserve the failed volume, restore
the selected verified FULL volume/DB+objects recovery point and its matching release,
start once, rerun D migrations/checks, and test two-account/history/CV/job state.
Do not run downgrade SQL, overwrite current data blindly, adopt anonymous records
or rewrite Git history. No restore has been performed by E. Deploy rollback alone
does not roll back a database schema. Test recovery on disposable hosted data first.

## One hosted scheduler path

deploy.runtime supervises `minder_app.hosted_worker.run(app)` in the same service
as HTTP. It calls D reconcile_notices(limit=50), then the existing A Worker.tick
every30 seconds. Reconciliation appends persisted unlinked outputs, never replays
processed actions. Worker uses existing leases/event IDs/retry limits. A completion
atomically stores a notice and D appends it once to the user's Mindbot singleton.
Worker failure shuts down the service so the configured bounded provider restart
policy can recover; logs contain status/code only. SIGTERM stops the polling loop
and allows30seconds for the current bounded operation. No browser timer or Mac cron.

Local actual worker checks cover due daily notice without browser, persistent
singleton message after Store reopen, duplicate tick no repeat, paused pending
event suppression and bounded retries. D's canonical automation contract and A's
worker integration also implement explicit cancel, saved schedule timezone,
owned-plan scope, next_run/last_result and today-only catch-up. E's ME2-R01 record
names the exact final integration checks and any remaining gaps. A hosted test must
close all browsers, wait for one due check, reopen, see one result in the SAME
conversation, pause/cancel another due check, retry/restart, and verify no action
replay. No hosted daily automation evidence exists yet.

## Cost and publication gate

Published Railway rates checked24Oct: RAM$10/GB-month, CPU$20/vCPU-month,
volume$0.15/GB-month, egress$0.05/GB. Existing plan minimum is an included-usage
commitment, not an extra fixed fee on top of all resource costs.
https://docs.railway.com/pricing

For a30-day illustrative resource budget: 1GB RAM +0.25average vCPU +0.5GBvolume
is $15.075/month or about$0.5025/day, plus egress, backups and applicable plan minimum.
This is a capacity scenario, NOT measured/billed host usage or an approved spend.
Verify actual app memory/CPU and account balance; set a permitted spending limit
before launching. No unconditional free-hosting claim. Clerk Hobby is advertised
$0 with prebuilt login and a50,000MRU/app limit; verify the actual chosen account
and do not enable paid add-ons. https://clerk.com/pricing . Groq remains within
existing authorized provider budget. No new subscription, SMS service or billing
upgrade is part of this candidate.

Publish the judge deployment only after A's accepted integrated SHA, actual resource
cost/access check, real two-account login/isolation/expiry/logout, full persisted
chat/CV/restart/recovery journey and hosted due-job test. User already requested
that scoped deployment; no repeat generic approval is needed. Missing access or
extra expenditure remains a concrete dependency, not permission to waive acceptance.
