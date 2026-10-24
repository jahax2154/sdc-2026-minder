# D native PostgreSQL and private Replit storage handoff

This extends A's `7d4073f0c8ce06faafff0bd97cfd94eb0444d93d` base. Existing SQLite/local/volume work is preserved. No anonymous records are imported or reassigned.

## Native database factory contract

`minder_app.postgres_store.PostgresStore.from_environment()` reads server-only `DATABASE_URL` and `MINDER_DB_SCHEMA` (default `minder`, validated identifier). Requires E's approved `psycopg[binary]==3.3.6`. It opens actual PostgreSQL connections; it never opens SQLite or treats a URL as a local path. Markers: `engine='postgresql'`, `persistence_mode='managed-postgresql'`, `durability_status='configured_host_acceptance_pending'`. Factory creation applies core tables; existing Application/services apply their additive migrations. Product migration **8** denotes the native PostgreSQL layout; existing SQLite remains **7**. Migration numbers 1–8 are present after full application initialization; a minimal Store alone initializes only its core tables.

Use A's `application_for_store(store, ...)` / guarded Replit composition. D changes no routes, shared schemas, providers or frontend files. The existing identity/conversation/generation/automation/Library public payloads remain unchanged. Persisted JSON stays text to preserve exact existing serialization, versions, immutable history and expected-version semantics. Schema-local advisory transaction locks preserve atomic writer check/write behavior across processes. Read snapshots use repeatable read. Provider calls stay outside transactions. Current SQL compatibility is deliberately limited to inspected service statements, not arbitrary SQLite SQL support. Unicode search preserves Python casefold and reads only owned visible message text; current prototype search scans an owner's active Minder history before pagination.

Connections use a five-second connect timeout and 15-second statement / ten-second lock limits. Nonlocal connections default to TLS `require`; explicit URL SSL configuration is honored. Error responses contain safe codes, never driver SQL/parameters/DSN. Native backups require a provider snapshot or operator `pg_dump`; SQLite backup is not silently substituted. Production backup/restore acceptance remains an operator dependency.

## Actual acceptance at this checkpoint

`docs/execution/product-v2/D/check_postgres.py` starts a disposable local **PostgreSQL 16.2**, runs the existing focused suite with native Store substituted for AppCase and reconnect fixtures, then stops/restarts that server and refetches JSON state in a fresh Python process. It requires test-only `pgserver==0.1.4`; this is not a runtime dependency. No live/shared DB writes, real profiles, actual login or model requests occur.

The focused suite passes **73 tests**: canonical native database service tests plus existing document-validation/local-storage fixtures. Covered: profile/plan/action/proposal/budget/worker records; generated/accepted plan state; automation state; concurrent identity mapping without anonymous adoption; one Mindbot under concurrent creation; Minder multiple histories/retries/deletion/search; server-owned outcomes; provider callback with another writer active; CV quotas/invalid formats/ownership/retry/extraction/deletion. Restart additionally preserves JSON booleans/null/numbers/timestamps and versions. This proves a real local PostgreSQL implementation, not hosted Replit availability.

## Remaining hosted configuration dependencies

E must supply an authorized Replit database connection and an isolated acceptance schema through server-side configuration, then verify the production database choice, two real managed identities, published restart/refetch and provider backup/restore. A URL or the engine marker alone is not acceptance evidence. No published app/production database/private bucket has been verified by D. Replit App Storage adapter follows as its own bounded checkpoint; Library remains explicitly unavailable unless selected and configured. No deployment, paid provisioning or shared live database mutation was performed by D.
