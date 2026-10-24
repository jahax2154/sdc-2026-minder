# One Replit Agent handoff — source import and guarded Python launch

User-selected target: Replit, existing Minder Clerk Development tenant.
This is preparation; no published Minder URL or deployed source SHA exists yet.

Read-only inspection identified editable project d8e6ee62-0e31-4863-bf19-b457893d558c,
currently old React/Node main4df6c08372e70ec0f60c844ccfc8bca19f119f1a. Do not publish
that source as Minder or change its history. The initial GitHub access check timed out; the later import preparation request
confirmed a Replit proxy requires GitHub connection, so no import was started.
User action: project Git pane / Connect to a Git provider / GitHub; authorize the
account with access to jahax2154/sdc-2026-minder, or use https://replit.com/import.
No credentials in chat. Existing project and public deployment are unchanged. Preserve the existing project while
importing actual official code. No new React/Express scaffold or auth tenant.

A's explicit porting base is42062878914c168752ae058cd4d4f09a37f9b26c. Its factory
contract is7d4073f0c8ce06faafff0bd97cfd94eb0444d93d; newer committed factory,
PostgreSQL/private-storage, E wrapper and F frontend handoffs must be included in
A's final publish-approved source. Neither porting base nor E prep tip is final
release approval. Stop before publish until A names the exact combined SHA.

For a fresh empty import directory, the concrete history-preserving PREPARATION is:

```sh
git clone --no-checkout --branch session/a-personal-integration https://github.com/jahax2154/sdc-2026-minder.git minder-release
git -C minder-release checkout --detach 42062878914c168752ae058cd4d4f09a37f9b26c
git -C minder-release rev-parse HEAD
```

Do not overwrite any existing folder. If GitHub authentication is required, request
connection through Replit's GitHub integration/import UI; no PAT/password in chat,
source or shell arguments. Do not force-push, rebase or push official main.
Once A supplies final accepted SHA, fetch the existing official branch and checkout
that exact full SHA in this isolated release directory; verify ancestry and HEAD.
Do not run/build the older base while describing it as the final combined release.

In the final release root, select Python3.12, integrate E's committed .replit/Nix
templates through A or deliberate provider configuration, then use:

```sh
bash deploy/replit/build.sh
bash deploy/replit/start.sh
```

Use the final release root as working directory; this is the actual Python backend
serving existing apps/frontend-product, not the root legacy Node project. Build
packs four existing verified O*NET artifacts, checks dependencies and CPU import.
No market crawl/scoring change/training or production DB write during build.

Provision/select the actual production PostgreSQL and private App Storage within
confirmed existing resources. Use D's existing semantics/native schema8 and
DocumentLibrary adapter. No SQLite/CVs on published filesystem or public CV URLs.
Use DATABASE_URL (server-only), explicit MINDER_DOCUMENT_STORAGE_BUCKET_ID, optional
PREFIX=minder/private/ and DB_SCHEMA=minder. Preserve current local data untouched;
no automatic anonymous account adoption or test fixtures imported into production.

User enters the existing Clerk public/server keys and Groq key ONLY in Replit
Secrets. Agent must not request/print/read back values. Use exact nonsecret fixed
runtime flags from deploy/replit/runtime.env.example. Startup derives public Clerk
issuer/signing key/origin without exposing server secret. Retain Qwen model/daily
cap; exact final HTTPS origin and existing `/` login/logout redirects, no wildcard.

Use one Reserved VM web deployment with one existing cohosted worker, only after
actual account allowance and machine quote are verified. Do not upgrade/purchase
or silently choose Autoscale. The connected publish tool reuses existing settings;
its default Autoscale behavior is unsuitable before VM selection is verified.

Report actual source HEAD, selected deployment type, DB/bucket presence, port8080
mapping and sanitized build/runtime results. Publish only final A-approved combined
source, then return actual URL/revision and verify real managed login, two-account
isolation, chat/CV persistence, restart/redeployment and a due worker event while
browsers are closed. Public health/local test counts alone prove none of these.
See deploy/replit/README.md for the full bounded run procedure and evidence limits.
