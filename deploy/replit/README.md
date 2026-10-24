# Replit — actual Minder Python app, hosted acceptance pending

Active target selected by the user: Replit. Existing Minder Clerk Development
application, existing vanilla frontend and Python backend, PostgreSQL plus private
App Storage. One Reserved VM web process with the existing cohosted persisted
worker, conditional on verified existing allowance; no automatic upgrade.

A explicitly identified porting base42062878914c168752ae058cd4d4f09a37f9b26c,
then published factory contract7d4073f0c8ce06faafff0bd97cfd94eb0444d93d. Later A
factory/portability and committed D/E/F handoffs must be integrated before A names
an accepted publish candidate. A porting base is not final release approval.

## Actual target inspection

Connected editable Replit project d8e6ee62-0e31-4863-bf19-b457893d558c:
https://replit.com/@yicheng070612/Aiversecity-Career-Compass . Read-only Agent
inspection found old React/Node source main4df6c08372e70ec0f60c844ccfc8bca19f119f1a,
no official team remote/Python Minder/Clerk, development PostgreSQL16.10 only,
no production DB/private bucket. Existing Autoscale URL is the older application,
not a Minder login deliverable. A second read-only GitHub import-access query timed
out; no result has established whether official repository access works there.
No remote source/config/database/bucket/publish mutation was made by E.

Account plan, remaining credits and actual Reserved VM quote are inaccessible to
these tools. User must inspect Publish (upper-right in project editor) / Adjust
settings / deployment type, or report that unavailable. Do not press purchase,
change plan or republish the old app to resolve this. Current official docs:
https://docs.replit.com/features/publishing/deployment-types

## Prepared commands and source contract

Use the actual imported official repository release root. Preserve official Git
history and the current Replit project snapshot. Never push Replit-generated
changes to official main. Root .replit/replit.nix installation is A-owned; templates
here require integration or deliberate provider configuration, not a source claim.

Select Python3.12 (available Python3.13 is incompatible with App Storage1.0.2).
Replit Publishing build command: `bash deploy/replit/build.sh`.
Run command: `bash deploy/replit/start.sh`.
Port8080 maps to public80. Nix template supplies GCC runtime libraries. The build
installs exact locked packages, packages/verifies only the four existing approved
O*NET inputs, checks dependency consistency and imports XGBoost3.4.1. It does not
run model training, migrations or provider generation during build.

A-approved same-version xgboost-cpu3.4.1 is selected only on Linux; other systems
keep generic xgboost3.4.1. Canonical foundation ranges remain constraints, all other
existing locked versions are unchanged. New approved dependencies: psycopg/binary
3.3.6 and replit-object-storage1.0.2 plus pinned transitive requirements. Resolver
selected48 Linux-compatible packages, CPU wheel, no generic XGBoost/NVIDIA package.
This is cross-platform resolution, NOT Linux execution or artifact prediction
proof. No approved learned-model artifact was copied into this source checkpoint;
actual target import/prediction checks remain where applicable. No scoring policy,
trained artifact, provider/model or numerical formula changes.

`python -m deploy.replit_runtime` requires A build_replit(), actual D PostgreSQL
store and the same-store private document library, verified server identity and
existing scheduled_worker. It fails closed without them. Existing threaded HTTP
keeps unrelated reads non-blocking; the supervised existing worker polls every30s,
reconciles saved notices and exits the service on worker failure. Health exposes
actual worker-thread liveness; a healthy thread is not a completed job proof.

## Private configuration and remaining account actions

Existing local file .env.deploy.local is ignored/untracked/0600 and opened in the
user's editor. Preserve values; user confirmation of saved keys precedes live key
checks. Locally, `python -m deploy.clerk_check` derives missing public fields and
checks public/server keys belong to the same existing Development instance using
bounded provider requests. It prints status only and explicitly does not claim
login or isolation. Public discovery needs no secret; backend instance/session
checks do. Never send secrets through Agent prompts or chat.

The Replit connector cannot transfer Mac secrets into Replit's Secrets tool. User
must enter CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY and existing GROQ_API_KEY privately
in the imported project's Secrets and ensure they are present in the published
runtime. Already-configured secrets stay sealed. Runtime derives missing public
issuer/signing PEM and exact authorized origin; optional overrides are listed in
runtime.env.example. No additional Clerk tenant/Replit Auth provisioning.

Provider production DATABASE_URL stays server-only. D requires explicit
MINDER_DOCUMENT_STORAGE_BUCKET_ID and optional PREFIX=minder/private/. Bucket
access must remain private and all downloads go through verified owner-bound
backend routes. Development database presence is not production provisioning.
MINDER_DB_SCHEMA defaults to minder; keep acceptance tests in a distinct owned
schema and never point tests at shared app tables. File bytes never live on the
published filesystem. DATABASE_URL must never become a Path/SQLite file.

Copy the nonsecret fixed flags from runtime.env.example, set actual accepted full
MINDER_RELEASE_SHA and final HTTPS MINDER_JUDGE_URL, then pin authorized parties to
that origin. Redirect paths in existing frontend/public config remain `/` for
sign-in/sign-out. Use actual maintained Clerk login/signup UI; no fake identities,
anonymous sessions, custom password storage or test-auth routes. Clerk Development
preview limits/posture apply; production/managed app enforcement remains enabled.

## Migration, recovery and release gates

D PostgresStore.from_environment() creates core native tables; A application and
product migrations apply through native schema8. SQLite remains schema7 and is
not automatically imported/reassigned. Existing local state remains intact; no
other lane database/profile/CV is exported. D preserves current JSON, versions,
history, owner mapping, action idempotency and scheduler leases. See
../../docs/execution/product-v2/D/REPLIT_PERSISTENCE_HANDOFF.md from repo root.
Run migrations as part of guarded application startup against the selected
production DB, never build against an accidental development/shared DB.

Before changes to a populated production database, verify Replit's production
backup/data-recovery capability for that selected DB and restoration to an isolated
acceptance target. Native Postgres backup uses provider snapshots/pg_dump, not
SQLite Store.backup. Private bucket recovery needs actual object restoration as
well as metadata recovery. Do not restore/drop production or claim backup survival
from local tests; provider recovery acceptance is still outstanding.

A must integrate and accept exact final combined source. Verify actual imported
Git HEAD, official remote and configured MINDER_RELEASE_SHA match that full SHA
before publishing. Do not use the old Replit source or an older accepted candidate.
Do not invoke the connector's default Autoscale first-publish flow for this worker.
Only reuse verified Reserved VM settings and existing allowance, then inspect build
and running health/revision. A publish submission alone is not a deployed success.

Required actual journeys: public URL -> signup/signin -> profile -> saved chat ->
supported fictional CV upload/download/extract/review -> logout/login -> records
preserved; two real accounts cannot read/write each other's records; expired and
revoked tokens denied; full restart/redeployment preserves database/CVs; one due
daily Mindbot result appears with browsers closed. Also exercise pause/cancel,
duplicate prevention and bounded retry through normal existing controls. No manual
Worker.tick, fake JWTs, local auth servers or browser credential export substitutes
for hosted proof. Report URL/deployedSHA, passing journeys and failures separately.

Current E preparation:15 focused deployment/auth-operator tests pass; actual Linux
execution, Replit prodDB/bucket, live Clerk journeys, final candidate approval and
hosted restart/scheduled-event evidence remain pending. SDK unit fixtures are not
real bucket evidence; D separately reports actual disposable PostgreSQL tests.
