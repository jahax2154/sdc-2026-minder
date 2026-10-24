# A-N6.0 — Replit lane release and exact backend factory contract

Source input for Replit porting:42062878914c168752ae058cd4d4f09a37f9b26c,
verified pushed on session/a-personal-integration and running locally9111. This is
a tested integrated BACKEND baseline, NOT an accepted final product/judge release.
F remains62fb94ffa8d2ad51f1415fa8b55cc9b70509a501; normal-onboarding browser step2
still has no starter cards. D starts fromd734d95cf68cb4945562bd9166714798edc2fb23;
E starts fromd6b18e3d0eb168ef1062f32e699c12e4fbbf6c8b. D/E should merge the
committed A bootstrap without dropping their own ongoing work. No other-worktree edit.

E reports the user's explicit hosting switch to Replit, Railway suspended; existing
Clerk Development/Qwen retained. E inspected legacy projectd8e6ee62-0e31-4863-bf19-
b457893d558c with old Node/React/main4df6c08372e70ec0f60c844ccfc8bca19f119f1a.
That published legacy app is NOT Minder. E reports only development PostgreSQL16.10,
no verified production database/private AppStorage or official repository import.
Account plan/credits/import access remain E inspection dependencies, not A assertions.
No new account request, subscription, machine upgrade or paid resources are approved
by this technical dependency handoff. E owns access, Replit wrapper/config and publish.

## A/D/E interface — engineering approval to implement

A exports application_for_store(store, *, role_ids=None, provider=None) in
minder_ml.intelligence.integration_cli. Trusted server composition only; reuses
actual catalogue, active scorer, market scopes, PublicRetrieval and Application.
Existing application(database,namespace,durable_root,...) keeps all local SQLite
isolation checks and delegates to the same common composition. No URL-as-path.

A exports minder_ml.intelligence.product_runtime.build_replit(*, store=None,
document_library=None). E imports build_replit() from its Replit Python wrapper,
then uses existing ProductServer/QuietHandler/web_app(app) and the existing
minder_app.hosted_worker.run(app, stop_event=...). One cohosted worker in one
Reserved VM. No duplicate scheduler/process/paid training/model probing.

D owns and will commit minder_app.postgres_store.PostgresStore(DATABASE_URL,
schema=MINDER_DB_SCHEMA or 'minder'). Required markers: engine='postgresql',
persistence_mode='postgresql', durability_status='configured_host_acceptance_pending',
volume_root=None; path never contains the DSN. A reads DATABASE_URL only from trusted
server environment and passes it directly to this constructor, never Path().
A-N6.0-R01 aligns the initial7d4073f proposal with D's actual early export.
It provides the ACTUAL Store API and connection/transaction SQL behavior used by
existing actions/worker/identity/generation/proposals, including current-version
and idempotency guarantees. Merely assigning these markers is not PG verification.
D owns SQL/schema/migration adaptation and all persistence modules; no A SQL rewrite.
D returns through DocumentLibrary.from_environment(store) when trusted env
MINDER_DOCUMENT_STORAGE=replit-app-storage. library.store must be that store;
library.backend().mode='replit-app-storage'. Implement existing put/get/delete
DocumentStorage protocol with opaque keys, immutable identical retries, bounded
private reads and owned routes. No public CV URL or local-filesystem durability claim.
The optional store/library arguments are trusted server/test injection only.

Required runtime env: MINDER_ENV=production, MINDER_AUTH_MODE=managed,
MINDER_AUTH_PROVIDER=clerk, MINDER_DOCUMENT_STORAGE=replit-app-storage;
GROQ_MODEL=qwen/qwen3.8-27b and existing private credential, plus D's DATABASE_URL
and MINDER_DOCUMENT_STORAGE_BUCKET_ID supplied through server-only configuration.
MINDER_DOCUMENT_STORAGE_PREFIX defaults to minder/private/. D publishes migration
commands and sanitized failures with its committed export.
No DATABASE_URL/key in browser bundles, Git, logs or cross-thread messages.
Clerk signature AND online active-session verification remain required. No local
anonymous login fallback. A factory sets managed_identity_required and binds the
existing Worker/real provider. It fails closed while D's committed adapter is absent.
Current SQLite production build_hosted/database-volume path is not Replit startup.

## Exact necessary dependencies

Approve psycopg[binary]==3.3.6 and replit-object-storage==1.0.2 for this bounded
port, Python3.12 retained. Verified public PyPI metadata: psycopg requires>=3.10;
Replit package requires>=3.8,<3.13, uses google-cloud-storage>=2.14,<3 and requests
>=2.31,<3. E owns deploy/requirements-hosted*.txt lock updates; D may install these
in its isolated environment for adapter tests. Approve pgserver==0.1.4 WITHOUT extras as a D-only isolated native PostgreSQL test
server (PyPI metadata verified; requires>=3.9). It is not a hosted runtime dependency,
new cloud database, shared DB write or production compatibility claim. Keep its
binaries/data/test schemas outside Git and stop only its owned local test server.
https://pypi.org/project/pgserver/0.1.4/ . No blanket pip/runtime upgrade,
new ORM, provider/model switch or architectural rewrite. Resolve/pin transitive
compatibility without changing existing unrelated packages. Package/API sources:
https://pypi.org/project/psycopg/3.3.6/ and
https://pypi.org/project/replit-object-storage/1.0.2/ .
Official Python API is from replit.object_storage import Client, with bucket_id,
upload_from_bytes, download_as_bytes and delete; D must bound reads/check opaque
keys and enforce ownership, rather than expose direct object access to clients.
https://docs.replit.com/features/sdks/object-storage-python-sdk

## Real hosting evidence required

Replit explicitly advises against durable data on published filesystem:
https://docs.replit.com/learn/projects-and-artifacts/replit-deployments .
Reserved VM supports always-on bots/background work:
https://docs.replit.com/features/publishing/deployment-types .
AppStorage is private but the app must authorize file access:
https://docs.replit.com/features/data-and-storage/object-storage .
No existing app/resource is changed by this handoff.

D must show real PG rollback/serialization/idempotent proposals and restart/history/
CV persistence on an isolated owned test database/bucket when access is available.
SQLite fixtures are composition tests, not PG acceptance. E must verify the actual
production DB/bucket/Clerk origin/access, resource budget and imported source SHA.
A integrates ONLY exact committed D/E/F handoffs and performs the new fresh-account
browser journey. Final publish-candidate approval/deployed URL follows those results;
4206287 is a porting base and does not waive the missing frontend/durable-state gate.
