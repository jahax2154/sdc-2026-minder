# A contract response to D — private-documents-v1

Dependency: D `1cb81b1574e1ef263a47e3bb0e098c50482340c5`, A bootstrap
`fbddeb80763442a8f1a4c8f8c2c80e4d6c4697a7`. This responds to D's coordination
request before shared edits. Storage/extraction is not implemented by A here.
Use the A commit containing this document as the additive contract dependency.

Confirmed scope: D owns documents.py, document_storage.py, their named test files
and migration6 in its existing sole product_migrations.py. OWNERSHIP.json now lists
the new files. A alone owns api.py and product_routes.py. No hosted storage/config
is verified; local private storage remains development-only. No deployment implied.

| Method/path | Strict request schema | Meaning |
| --- | --- | --- |
| GET /api/product/documents | Empty object | Owner-scoped metadata and actual limits/capabilities |
| POST /api/product/document-upload | DocumentUpload | filename, content_type, content_base64, idempotency_key |
| POST /api/product/document-download | DocumentRead | document_id only; authenticated base64 response |
| POST /api/product/document-delete | DocumentDelete | document_id, expected_version, idempotency_key |
| POST /api/product/document-extract | DocumentRead | document_id only; TXT to existing private review draft |

Schemas are additive definitions in contracts.schema.json. Same bearer owner and
sanitized `{code,request_id}` errors; Cache-Control:no-store. Never accept a user
owner/path/fetch URL. Metadata includes opaque document_id, version, filename,
declared/validated content type, byte size, created time and explicit extraction
availability. Download adds base64 content, never a public filesystem URL. A list
must not include raw content. D publishes exact response examples in its handoff;
F uses only advertised implemented operations, not an optimistic pending flag.

TXT/PDF storage and download do not establish parsed competence or supported PDF
extraction. TXT extraction creates/reuses an owner-scoped review draft; it never
saves Profile/evidence automatically and must reject content beyond the existing
64KiB intake contract. PDF extraction returns explicit unavailable, with no provider
request. Repeated extraction should return the same surviving review draft;
delete invalidates future document access. D records draft-retention semantics
explicitly; no claim that deleting a source rewinds already reviewed Profile data.

## Bounded defaults and transport

Defaults confirmed: **65536 bytes/file,10 files/owner,524288 bytes/owner**. These
are engineering resource limits, not product evidence/scoring rules. D is the
single owner of server-only limit configuration, decoded-byte/file-count/quota
enforcement and its validation. No request body can increase a limit. The bounded
prototype's per-file maximum is1048576 bytes (1MiB), independent of user quota.
If a future scope needs more, publish a new bounded transport policy first.

D exports `upload_request_limit()` from documents.py:

```python
return max(131072, 4 * ((configured_max_file_bytes + 2) // 3) + 4096)
```

Configured max bytes must be a validated positive integer <=1048576. The4096-byte
allowance covers bounded JSON metadata and whitespace. Base64 must be strictly
decoded/validated, and D checks actual decoded bytes, not declared length. A's
WSGI parser uses this helper **only for POST document-upload**, rejects invalid
helper returns and never exceeds1402200 bytes. All other routes retain131072.
Before D exports the helper, upload also retains131072; default64KiB fits. This
transport cap bounds requests only: D enforces actual file format, owner quota,
atomic retries, safe opaque paths, no symlinks/traversal and deletion cleanup.
Never derive storage paths from submitted filenames or return private paths/errors.

Keep storage under the current lane's isolated ignored product/uploads directory,
permission-restricted; no real-user uploads in Git/tests. Cross-user list/download/
extract/delete, malformed base64, content-type/signature mismatch, retry conflict,
stale delete, quotas, cleanup failures and unavailable PDF extraction need D tests.
F previews escaped filenames/text, never uploaded HTML or inline active PDF code.

## Committed handoff and integration repair

D can consume this A contract commit by normal merge, preserving current work;
do not cherry-pick already included state checkpoints. Return a full tested SHA,
response examples, exact configuration names and storage/retention limits. No
shared contract/API edits from D. A will integrate only committed document changes.

Known existing repair for D: test_product_state.test_wsgi_contract_status_and_
unavailable_states assumes E `/api/product/views/news` is unavailable. After E
`c2628eceaf4700cd124a407ec4dfe43a6cdbd4ff`, it is a real ProductView. Please repair
that owner-controlled assertion in a focused D3.1-R01 checkpoint by asserting
capability-consistent behavior; preserve isolated-D coverage. A will update its
own bootstrap assertions separately. This is an obsolete check, not permission
to ignore an unresolved full-suite failure or change the implemented E response.

Publication: A pushes its contract/integration branch; D publishes only D's branch.
No hosting access was found or provisioned. No credential/DB/source copying.
