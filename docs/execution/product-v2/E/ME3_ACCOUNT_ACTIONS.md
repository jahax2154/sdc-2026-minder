# Railway/Clerk operator preparation — actual account access still pending

Prepared from committed A `0a39b392b1f2b594abb8b23a4f0a8f73a4bec0c4` while A/F
continue application repairs. This is NOT an approved judge release or a deployed
revision. E requested A's explicit final integrated source approval; no approval
record or deployment has been invented from an older accepted snapshot.

## Exact user account actions

1. Open the intended EXISTING Railway project. In project Settings / Tokens create
   a project token scoped to its deployment environment. Put it in the ignored
   owner-only private file below as RAILWAY_TOKEN. Use the project command palette
   to copy project/environment/service IDs into the corresponding fields. Confirm
   existing credits and the available limit in MINDER_DEPLOY_MAX_USD; no upgrade,
   top-up or new plan. If no existing project/resources exist, report that fact.
2. In that Railway service attach the permitted persistent volume at `/data`.
   Keep one replica and serverless/sleeping OFF. No independent cron service or
   second SQLite volume. E checks the actual target and attachment before deploying.
3. In Clerk Dashboard select the intended application's PRODUCTION instance.
   Configure an existing owned domain and complete its DNS records. The application
   origin must match the production-domain setup; a Railway-generated subdomain
   alone does not satisfy Clerk's owned-domain prerequisite. No domain purchase or
   paid feature is authorized. If no existing domain is available, report it so the
   production-access dependency can be resolved explicitly; do not silently use a
   development realm or local auth bypass as production.
4. Clerk / API Keys: save the matching live publishable key, live secret key,
   JWT PEM public key and exact HTTPS issuer in the same private file. Set
   CLERK_AUTHORIZED_PARTIES to the actual app HTTPS origin and MINDER_JUDGE_URL to
   that origin. Leave CLERK_AUDIENCE blank unless that actual session template
   issues it. For a multiline PEM, use a double-quoted value with literal `\n`
   separators; the operator parses it as a string, never as shell code.
5. Clerk / Users: provision two distinct dedicated acceptance accounts. Save their
   opaque user IDs as CLERK_ACCEPTANCE_USER_A/B in the private file. Actual sign-in
   happens through maintained provider UI; passwords/email codes never go in chat.
6. Save the existing authorized Groq key as GROQ_API_KEY in the private file or
   directly in Railway service / Variables. Preserve qwen/qwen3.8-27b and the
   existing daily limit. No key is copied automatically from another lane.

**Private location:**
`/Users/phuahjunhong/sdc-2026-minder-worktrees/session-e/.env.deploy.local`

The file was created empty with0600 permissions and is covered by the existing
`.env.*` ignore rule. It contains placeholders only at this checkpoint. The provider
Variables interface is also a private configuration location. Never send its
contents, credentials, session cookies or tokens in chat, screenshots or Git.

Official account setup references:
https://docs.railway.com/integrations/api (project tokens are environment-scoped)
https://clerk.com/docs/guides/development/deployment/production (owned domain/DNS)
https://clerk.com/docs/guides/development/managing-environments (separate realms)

## Independent preparation completed

- Official Railway CLI5.71.0 installed and version/help verified in the temporary
  E-only path `/private/tmp/minder-e-railway-cli/node_modules/.bin/railway`.
  No global install, account signup, service/volume creation, variable change or
  deployment was performed. The Railway plugin is available but not installed;
  the scoped project-token route works independently of that plugin.
- `deploy.operator doctor` reports only missing field names and capability state;
  it never prints secret values. Latest run still reports14 missing setup fields.
  Private configuration requires an owned regular0600 file, rejects symlinks,
  unknown/test-bypass fields and never executes shell syntax; values are literal data.
- Operator inspect verifies the token's exact existing project/environment/service
  and a single matching `/data` attachment. Current provider input schemas are
  inspected before settings changes. Actual provider verification remains pending
  credentials; schema/account tests use controlled responses and claim no live access.
- The mutation/deploy path requires an explicit A approval record, a full approved
  SHA reachable in the official published A branch, positive finite authorized
  budget and valid live Clerk configuration. It checks public-key/issuer alignment,
  parses the signing PEM and preserves strict managed/private-volume runtime mode.
  Provider-token and acceptance-user fields are never copied into app variables.
- Private variables use a JSON request with skipDeploys, preserving other fields;
  no secret command arguments/output. The CLI uploads a fresh `git archive` of
  EXACTLY the approved commit, never the active checkout/private/untracked files.
  Explicit existing IDs, token verification, CI mode, closed stdin and no --new /
  --yes flags prevent the CLI's new interactive signup/creation flow.
- Public live probe checks the actual HTTPS origin, health revision, managed public
  config, unauthenticated private reads401 and anonymous /api/session401. It
  explicitly marks live login/two-account/restart/daily checks false; those cannot
  be inferred from public health. No local test identities are accepted or exposed.

Nine operator/deployment tests pass in isolated Python3.12. They cover private-file
permissions/redaction, target mismatch, missing/NaN/infinite budgets, wrong volume,
runtime-only variable allowlists, live realm/origin mismatch and anonymous bypass
rejection. No production request or actual deployment is claimed by these tests.

## Commands after private setup and A approval

```sh
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m deploy.operator doctor
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m deploy.operator inspect
```

E creates `deploy/RELEASE_APPROVAL.json` only after A explicitly names the accepted
integrated source for deployment. Required fields: approved_by A, approved_for
judge_deployment, approved_sha full40hex, approval_reference identifying A's actual
approval. No sample approval file is installed; missing approval fails closed.

Then use operator prepare-service / deploy, reconcile the actual provider status,
and run `python -m deploy.live_probe`. A submitted build is not a healthy deployment.
Do not automatically replay an uncertain provider mutation/upload; inspect the last
deployment first. Existing Docker build/start, data packaging, migrations/backup,
worker supervision and cost assumptions remain in deploy/README.md.

Actual remaining acceptance is performed with real managed accounts through the
normal UI/API: two-user isolation, saved visible chat, supported synthetic CV
upload/download/review, full restart persistence and one due hosted worker result
while browsers are closed. No browser credential export, fake signed identities,
test-auth server, schema bypass or manual Worker.tick may substitute for hosted
proof. A/F's ongoing model and UI repairs are accepted separately by A.

Public URL: unavailable. Deployed SHA: unavailable. Live journeys: not run, gated
on the actual account/domain/volume setup and approved source. All original raw/
derived inputs and private state remain excluded/unbacked-up by source commits.
