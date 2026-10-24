# ME4 — existing Minder Development instance and private operator setup

E reconciled by fast-forward to A `c7953a378871e1293760cf24757ab4c47f6c6dbe`,
a descendant of accepted `40d55c22b87b5e67ea1d32a1801b83e3527f2c2d`.
No older source replaces A's latest repairs. Further A repairs need their own
accepted source before deployment; the current checkout is not implicit approval.

## Private file

`/Users/phuahjunhong/sdc-2026-minder-worktrees/session-e/.env.deploy.local`

Existing values preserved. Verified owned regular file, mode0600, Git-ignored
and untracked. Opened in the installed Visual Studio Code app. Do not paste its
contents or any account/session credentials into chat or source control.

These are the exact accepted private operator fields; no NEXT_PUBLIC/VITE aliases
are used by this Python/vanilla integration:

| Variable | Value/location and consumer |
| --- | --- |
| CLERK_PUBLISHABLE_KEY | Copy Minder / Development / API Keys publishable key (`pk_test_`). Used for existing ClerkJS and backend setup. Public. |
| CLERK_SECRET_KEY | Copy SAME instance's secret key (`sk_test_`) into file or Railway Variables if missing. Server-only; required specifically by existing online `sessions.get` status/subject check after JWT verification, including prompt logout/revocation denial. Public discovery never needs it. |
| CLERK_ISSUER | Leave blank for derivation from publishable key's Frontend API host. Backend verifies exact issuer. |
| CLERK_JWT_KEY | Leave blank for public JWKS discovery/conversion into RSA PEM. If more than one key exists during rotation, select the current PEM under Clerk API Keys / Show JWT Public Key rather than guessing. Backend verifies signatures locally. |
| CLERK_AUTHORIZED_PARTIES | Leave blank for derivation from MINDER_JUDGE_URL. Exact HTTPS browser origin, no wildcard/trailing path. Backend verifies azp and Origin. |
| CLERK_AUDIENCE | Leave blank unless actual session token configuration deliberately emits that audience. |
| MINDER_CLERK_INSTANCE_MODE | Already `preview`; operator enforces matching test realm keys. Not sent to the app. |
| RAILWAY_TOKEN | Railway existing project / Settings / Tokens: environment-scoped project token. Operator only, never app/browser variable. |
| RAILWAY_PROJECT_ID | Existing project ID, copied from Railway project settings/command palette. |
| RAILWAY_ENVIRONMENT_ID | Selected existing environment ID from Railway. Must match token scope. |
| RAILWAY_SERVICE_ID | Existing Python service ID from Railway. Must belong to selected project/environment. |
| MINDER_JUDGE_URL | Service / Settings / Networking: existing generated HTTPS Railway domain; generate one if absent. Origin only. |
| MINDER_DEPLOY_MAX_USD | User-confirmed available allowance within existing credits/resources; no plan/top-up upgrade. Operator checks acknowledgement, not an automatic provider billing cap. Actual cost verification remains required. |
| GROQ_API_KEY | Existing authorized key, private file or Railway service / Variables. Already sealed values stay there; never export to browser. |
| GROQ_MODEL | Preserve `qwen/qwen3.8-27b`. |
| MINDER_LLM_DAILY_LIMIT | Preserve existing agreed limit; template default20. Not a provider rate-limit bypass. |
| CLERK_ACCEPTANCE_USER_A | Optional private acceptance record of first real user ID; not a runtime secret or deployment prerequisite. |
| CLERK_ACCEPTANCE_USER_B | Optional second distinct real user ID; not a runtime secret or deployment prerequisite. |

Runtime variables set by operator (not additional user file entries):
`MINDER_ENV=production`, `MINDER_AUTH_MODE=managed`, `MINDER_AUTH_PROVIDER=clerk`,
`MINDER_DATA_ROOT=/data`, `MINDER_DB_PATH=/data/minder/runtime.sqlite3`,
`MINDER_DOCUMENT_STORAGE=private-volume`,
`MINDER_DOCUMENT_STORAGE_ROOT=/data/minder/documents`, `MINDER_RELEASE_SHA=<approved SHA>`.
Railway supplies PORT and actual RAILWAY_VOLUME_MOUNT_PATH from the attached volume.
Do not fake that mount variable. One replica, sleep/serverless off; web and existing
worker share that same service and durable volume, no independent SQLite cron.

## Derivation and continuation

After saving the publishable key, E can run without a secret:

```sh
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m deploy.operator derive-clerk
```

This only contacts the decoded public `*.clerk.accounts.dev/.well-known/jwks.json`
endpoint over HTTPS, rejects redirects, bounds response size and accepts one RSA
signing key. It preserves nonempty values and refuses an issuer mismatch. No
Backend API call, Authorization header, cookie or secret key is used for discovery.
Fill only blank issuer/public PEM/origin fields; never overwrite saved configuration.

Once Railway URL is saved, rerun to fill authorized parties. Clerk redirects use
this exact HTTPS origin and existing frontend paths `/` for sign-in/sign-out.
Reuse Minder's managed components; no additional Clerk application, custom password
flow, fake Clerk test users or local authentication bypass. Dedicated real users
sign in through existing maintained Clerk UI. Preview uses Clerk's Development
instance posture/limits; app still enforces production/managed private access.

Provider inspect, A's exact accepted source, actual volume, cost and current service
configuration must be verified before deployment. Then run public boundary probes,
actual sign-in/two-user cross-access/logout/expiry checks, chat and supported CV
save/download/review, full service restart survival and a due daily event while
browsers are closed. Public health or controlled unit identities prove none of
those real managed/hosted journeys. No live deployment claimed at this checkpoint.

Official derivation reference:
https://clerk.com/docs/guides/sessions/manual-jwt-verification
https://clerk.com/docs/guides/how-clerk-works/overview

Verification: ten deployment/operator tests pass, including secret-free discovery,
preservation of private values/comments, no Authorization header, rejection of
non-Clerk discovery targets, key-rotation ambiguity and stale editor snapshots.
No provider secret is required by doctor/public discovery. Existing SDK identity
verification and strict server revocation behavior are unchanged.
