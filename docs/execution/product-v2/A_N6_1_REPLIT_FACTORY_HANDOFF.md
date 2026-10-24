# A-N6.1 — concrete Replit composition hook, D/E released

Continues the verified porting base42062878914c168752ae058cd4d4f09a37f9b26c,
contract7d4073f0c8ce06faafff0bd97cfd94eb0444d93d, D-export refinementfe120a1
and provider portability refinementc5ea43a7dbc856228a70d4389d045d505e6a5597.
Use the commit containing this handoff (normal descendant), not the obsolete
Railway mounted-SQLite startup path, for D/E integration. It is not final product
or judge acceptance; F's mandatory starter UI connection remains missing.

Implemented exact exports:
- integration_cli.application_for_store(store, *, role_ids=None, provider=None)
- product_runtime.build_replit(*, store=None, document_library=None)

The local SQLite application factory retains isolation checks and delegates to
the same common composition. The new Replit factory requires production/managed
Clerk/private AppStorage server configuration before any D construction. It imports
D's actual early interface PostgresStore(DATABASE_URL,schema=MINDER_DB_SCHEMA or
'minder'), checks engine/persistence_mode='postgresql', builds the unchanged source
catalogue/scorer/current-market services and real PublicRetrieval, and binds the
same Qwen coordinator, owner budget, canonical migrations, managed route boundary,
private DocumentLibrary and existing Worker. E starts that worker once using its
owned wrapper. A does not launch a new worker/service or touch another worktree.
Library/store identity and backend mode replit-app-storage are required. Missing D
module fails D_postgresql_store_handoff_not_integrated; SQLite/local-document
fallbacks are rejected. A never interprets DATABASE_URL as a filesystem path.

D owns SQL/migrations/store/documents/storage and real PostgreSQL semantics. Row
access must support both named and positional access; audit actual rowid ordering,
INSERT OR IGNORE/REPLACE, json_extract/julianday, savepoints and transaction/version/
idempotency serialization. No source-string substitution alone is native evidence.
D's isolated pgserver==0.1.4 WITHOUT extras is approved solely for native local tests;
psycopg[binary]==3.3.6 and replit-object-storage==1.0.2 are the necessary Python3.12
pins. E owns hosted requirements lock and Replit wrapper, resource/access checks,
actual production DB/private bucket configuration, import revision and publication.
MINDER_DOCUMENT_STORAGE_BUCKET_ID is required; prefix defaults minder/private/.
No live/shared DB writes, credential export, broad upgrades or new paid resources.

## Verification and explicit limits

204backend checks pass12.775s, including6new factory checks. They verify config
fail-closed, missing D adapter, SQLite rejection, actual constructor URL/schema
forwarding, common app/provider/worker/private storage wiring and managed boundary.
The successful injected adapter checks are DECLARED SQLite-backed composition
fixtures, not a PostgreSQL compatibility, live Clerk, object-store or hosting claim.
No native provider request occurs. Existing10deploy regressions also pass0.155s.
Logs replit-composition-d-contract-full.log and replit-unchanged-deploy-regressions.log
remain in ignored A artifacts. No live DB, bucket, Replit project or environment was
modified. A's currently running localhost remains the verified4206287 runtime;
this new hosted hook is unused until the committed D/E handoffs are integrated.

E inspected a legacy Replit Node/React project; it is not the current Minder source.
Repo import, actual production database, private bucket, current account resources,
Clerk origins and hosted acceptance remain unverified. Do not publish a success
claim or create a fresh account to bypass access. Existing plan/history/CV semantics
remain mandatory. A will integrate D/E/F exact committed missing changes, then run
the complete fresh-account browser journey and scoped hosted acceptance. Main is
not merged and no deployment is performed by this checkpoint.
