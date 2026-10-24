# D4 document library — early interface export

Version: private-document-library-v1. A confirmed the shared interface at3561e93d1bae4ec78fd661e0729fbf53322252c4
before D implementation; shared changes remain A-owned. D owns documents.py, document_storage.py, migration6 and tests. A alone
registers/publishes HTTP routes and changes transport caps; F owns the frontend.
This first checkpoint implements the storage interface/validation; HTTP operations
remain unadvertised until implemented and A-registered. Existing auth/error envelope.

| Method/path requested from A | Strict body | Result |
| --- | --- | --- |
| GET /api/product/documents | empty | {contract_version,documents,limits,storage} |
| POST /api/product/document-upload | filename,content_type,content_base64,idempotency_key | {document} |
| POST /api/product/document-download | document_id | {document,content_base64,download_content_type:'application/octet-stream'} |
| POST /api/product/document-delete | document_id,expected_version,idempotency_key | {document_id,status:'deleted',deleted_at} |
| POST /api/product/document-extract | document_id | {document,extraction:{status,reason?,manual_entry_available:true},draft:null|existing intake draft} |

Strict request schemas are exported as documents.SCHEMAS. Metadata document fields:
document_id,filename,content_type,size_bytes,sha256,created_at,version,status,
extraction_status. No storage keys, owner IDs, paths or private text in list metadata.
Statuses: uploading,active,deleting. Deleted records disappear from list/download.
Extraction states: not_requested,review_available,unavailable. List limits include
max_file_bytes, max_files, max_user_bytes, upload_request_bytes. Counts include
uploading/deleting reservations until deletion actually finishes.

PDF/TXT only: matching extension and MIME; strict base64; nonempty bytes. TXT must
be UTF-8, no binary controls. PDF signature/EOF checks are format screening only,
not a malware scan or full parser. F downloads as attachment via Blob/application
/octet-stream; never embed/execute PDF/text or put bearer tokens in URLs.

Default limits64KiB/file,10 files,512KiB/user. Environment overrides:
MINDER_DOCUMENT_MAX_FILE_BYTES (1..1MiB), MINDER_DOCUMENT_MAX_FILES (1..100),
MINDER_DOCUMENT_MAX_USER_BYTES (1..64MiB). Transport envelope required from A:
max(131072,4*ceil(max_file_bytes/3)+4096) for upload route only, with existing131072 elsewhere.
No user can configure limits or select a storage path in a request.

Storage interface DocumentStorage: put(key,bytes), get(key,max_bytes), delete(key).
Opaque server keys only. put retries immutable content; delete returns only when
absent, missing object is idempotent. LocalDocumentStorage is development-only,
0700 root and0600 files, denies symlinks/traversal and bounds reads. No hosted
implementation selected: no verified host/private bucket/durable volume is present.
Default storage is disabled; operator explicitly sets
MINDER_DOCUMENT_STORAGE=local-development to use reserved lane uploads/documents.
Optional MINDER_DOCUMENT_STORAGE_ROOT must be an absolute private path outside any
public web root; no durable-hosting claim. Hosted support requires a verified host,
private bucket/volume/access policy, scoped server credentials and durable DB
configuration. No whole-document provider call is part of any operation.

Storage, extraction and profile apply are separate actions. TXT extract reuses
intake_draft <=64KiB and returns reviewable private text; PDF extraction and oversized
TXT extraction explicitly unavailable. Upload never applies profile changes. Existing
POST /api/product/intake-correction is the only reviewed apply path; manual profile
entry remains independent when storage/extraction unavailable.

Target deletion semantics: quarantine metadata first; purge linked intake drafts at
that point, then idempotently delete stored bytes; storage failure leaves deleting
state and retryable same delete request, never a false success. Completed deletion
scrubs file metadata to a minimal tombstone. Profile fields already explicitly
reviewed/applied, profile history and their existing authority/retry records remain;
document deletion is not account/profile erasure or physical backup/WAL sanitization.
Pending derived drafts cannot be applied after deletion begins. A deleted upload
receipt cannot re-create the file on retry. No public URLs or logging of bytes/text.

D4.1 check:6 focused storage/format/configuration tests passed. This checkpoint
contains only tested interface/validation/storage; operation activation follows in
D4.2. A confirmed no hosted storage; missing dependency stays explicit.
