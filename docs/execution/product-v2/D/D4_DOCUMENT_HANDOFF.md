# D4 — private document library handoff

Implementation complete for the bounded local prototype; hosted storage unavailable.
All new migration SQL remains D-owned. A approved/published the shared interface
before implementation; F retains frontend ownership. No deployment, provisioning,
paid infrastructure, external fetch or whole-document provider request occurred.

| Checkpoint | Scope | Verification |
| --- | --- | --- |
| A3561e93d1bae4ec78fd661e0729fbf53322252c4 | Approved routes, ownership, canonical inputs, bounded upload transport | A-owned3 transport tests consumed/passed |
| D989480fa0386a8a6ddcd73e9c818938904bc7f68 | D3.1-R01 capability-consistent E-news test | 8 D state tests |
| D9605f496c226b2275ebc767b87ec9a9899f1d0e2 | D4.1 early contract, validation, local storage boundary | 6 focused tests |
| Da526558ce79b98e073d7a3316c1a94ea1adcef81 | D4.2 library operations, ordered migration6, reviewed TXT reuse | 72 backend /20 focused /3 transport |
| D5c3886957f1f7b30e84a3f12743ef8fcb4648b93 | D4.2-R01 exact A schemas; corruption regression | 73 backend /21 focused /3 transport |
| Commit containing this record | D4.3 synthetic WSGI examples and final handoff | check_documents.py passed, no private bytes/text exported |

Branch: session/d-profile-state. Integrate its final full SHA, which includes all
above dependencies, rather than active worktree files. D returns the final remote
SHA in its completion message to A/F. No main merge/force push/deployment.

## Actual transport and integration

Five operations registered by A, implemented by D:
GET /api/product/documents;
POST /api/product/document-upload, document-download, document-delete, document-extract.
All use existing bearer owner, JSON/error envelope, Cache-Control:no-store.
Upload/download bytes are base64 JSON, never public URLs. Strict requests are
A's canonical DocumentUpload/DocumentRead/DocumentDelete definitions, re-exported
by documents.SCHEMAS. Exact outputs are in D4_DOCUMENT_CONTRACT.md / D4.2.md;
observed synthetic metadata/empty/unavailable/errors are in document-response-examples.json.
Private file bytes and extracted text are deliberately excluded from that export.

A: normal integration applies migrations1–5 then additive6 through existing
product_runtime.build. Fresh/disposable-v5 upgrade tests preserve existing profile,
history and product retry records. Metadata, retry hashes and source/draft links live
in the existing SQLite database. No mirrored user/profile store or replacement DB.
A's route-specific upload cap consumes documents.upload_request_limit(); all other
requests keep131072 bytes. Shared definitions/registration were never edited by D.

F: first check GET documents.storage.status and actual limits; do not enable upload
when unavailable. Registry 'implemented' describes handlers, not configured storage.
Render status uploading/deleting and unavailable extraction honestly. Use exact
request key/body for retries; saved metadata.version changes on extract, so refetch
or use the returned document.version for delete. Remember a failed delete's original
body/key to resume it; starting another delete while deleting fails409. Downloads
must use a Blob/application/octet-stream attachment, never inline active content.
Render filenames/extracted text as escaped text, not HTML. TXT extract returns the
existing intake draft; users choose structured fields for existing intake-correction.
Uploading a document does not itself parse it or alter profile/skill evidence.

## Configuration and hosting dependency

The checkout contains no verified hosted private-storage adapter/deployment config.
Existing TEAM_START/CAPABILITIES/LAUNCH explicitly describe local-only runtime and
unverified hosted auth/storage. No .replit/container hosting configuration was found.
No host credentials were copied, logged or provisioned. Default storage is disabled.

To enable only the existing local development adapter before server start:

```sh
export MINDER_DOCUMENT_STORAGE=local-development
```

It uses the current lane DB parent's uploads/documents, e.g. D's
ml/artifacts/session-d/product/uploads/documents. Optional absolute
MINDER_DOCUMENT_STORAGE_ROOT must remain inside that same lane uploads subtree.
Root0700, blobs0600, opaque server-generated keys; no filenames become paths.
LocalDocumentStorage reports durable_hosting_verified:false. This flag cannot be
turned into hosted verification by configuration. Unknown storage modes fail closed.

Server-only optional limits (positive integers):
MINDER_DOCUMENT_MAX_FILE_BYTES=65536, maximum1048576;
MINDER_DOCUMENT_MAX_FILES=10, maximum100;
MINDER_DOCUMENT_MAX_USER_BYTES=524288, maximum67108864.
Reservations count against quotas even while upload/delete is incomplete.
List reports configured limits and usage. Client request fields cannot override them.

Precise hosted dependency: A/operator must identify the actual hosting runtime and
its existing private bucket or durable volume, server-only scoped credential source,
object namespace/access policy, and durable backing for the existing DB. Then an
adapter implementing put/get/delete can be configured and verified for private
reads, restart persistence and deletion. No hosted provider was selected absent
that information; setting a generic hosted mode currently returns
 document_storage_backend_not_configured. Independent local work is finished.

## Deletion and untrusted-input behavior

Deletion first persists deleting and removes linked drafts/source links, blocking
new reads/extraction and any pending review apply. File bytes are then removed;
only after successful storage deletion is metadata reduced to a minimal deleted
ID/status/time tombstone and quota released. Exact retries return the same deletion
result. A storage failure returns sanitized500 with deleting still visible/retryable,
bytes potentially present but inaccessible through library operations. Retrying the
original upload after deletion fails404 rather than recreating data.

Reviewed fields already explicitly applied to Profile, profile/history/authority
records and existing correction retry receipts remain. Document deletion does not
undo user-confirmed profile edits or erase SQLite free pages/WAL/external backups.
No secure-erasure, legal retention, automatic expiry or whole-account deletion claim.
Standalone intake drafts created without a library source are not affected.

TXT extraction reuses the existing <=64KiB reviewed-intake implementation. PDF and
larger TXT extraction return unavailable with manual_entry_available:true. PDF/TXT
format screening is not malware scanning/full PDF validation. Stored content is
untrusted bytes; no tool/action authority, automatic competence inference or profile
application follows from it. No Groq call is made by upload/extract/download/delete.
Manual structured profile entry remains usable with storage/extraction disabled.

## Reproduction and observed coverage

From D, use the existing read-only Python environment:

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests "$MINDER_PYTHON" -m unittest test_documents test_document_storage test_product_migrations test_profiles
PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests "$MINDER_PYTHON" docs/execution/product-v2/checks/test_document_transport.py
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/D/check_documents.py
```

Observed21 focused tests,3 A transport tests,73 backend tests passed. Synthetic
WSGI runner passed upload/list/download, exact retry, cross-owner isolation,
TXT review reuse, restart/refetch, stale delete, file/draft deletion, non-resurrection,
PDF unavailable and manual entry, with zero provider calls. Other tests cover
formats, path/symlink denial, byte/count/user quotas, private permissions,
write/read/delete failure states, checksum corruption and larger bounded transport.
No server/TCP listener or private real-user file was needed. Disposable D-only
file/DB state is cleaned by the runner. Recorded examples are synthetic metadata.

Preserved unrelated untracked ml/minder_ml_starter/{raw,derived}; excluded and
not backed up by D. .env.local, actual runtime SQLite, uploads and caches remain
uncommitted local state; no backup/durable hosting claim. Only reviewed task source,
tests, schemas already A-published and reports are in these checkpoints.
