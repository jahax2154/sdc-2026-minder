# MD2 — CV/resume purpose, supported PDF text extraction and reviewed changes

Implemented local/service slice; actual hosted storage/login/restart remain gated
on E's missing account/volume/Clerk configuration. Dependency Afa1130 canonical
DocumentUpload.purpose and Profile.onboarding; D mounted boundaryc24c100. Schema7
unchanged; metadata remains in existing library tables and drafts, same database.

New uploads REQUIRE purpose:'cv'|'resume', from A's strict schema. Metadata retains
purpose plus purpose_basis:'user_declared_not_independently_verified'. This restricts
the product flow to declared CV/resume; extension or declaration is not independently
verified document semantics. Other declared purposes/missing purpose are rejected.
Legacy files remain legacy_unclassified, downloadable/deletable; they are never
silently relabelled CVs or assigned to a new logged-in owner. New extraction of
unclassified legacy sources is unavailable; manual profile entry remains available.

TXT <=64KiB still uses the existing reviewed intake, not a second profile extractor.
PDF text extraction uses A-approved pypdf>=5,<7. Without the installed dependency,
PDF extraction remains explicitly unsupported. With it, list returns
extraction.pdf_status:'supported_text_only' and supported_types includes application/pdf.
No mandatory OCR. Scanned/empty, encrypted,>20-page, oversized-text, malformed,
timeout/budget and busy states have explicit unavailable reasons and manual entry.
Uploads are still bounded<=configured max1MiB; extracted UTF-8 text<=64KiB.

Parsing is a separate bounded child process:2 concurrent slots,12s wall timeout,
5s CPU limit,384MiB address-space limit on Linux,20 pages,2MiB decoded content
stream/page cap. pypdf can require substantial memory for content streams, so parsing
is isolated from the web/worker and no write transaction spans it. Child receives
only bytes via pipe and PATH/PYTHONPATH/LANG; server credentials are not inherited.
Captured parser stderr is discarded, never exposed/logged. No PDF executes tools,
fetches resources or invokes Groq. This is not malware scanning or full semantic CV
verification. Technical basis: https://pypdf.readthedocs.io/en/stable/user/extract-text.html

A review draft adds source_document_id/source_content_type/source_sha256 and keeps
its document-claim provenance. Repeated/concurrent extraction reuses one surviving
draft; applying selected structured fields is still existing /intake-correction.
Parsing revalidates source ownership/status afterward; deletion during parsing
cannot resurrect a draft. Deletion purges linked pending/reviewed drafts, deletes
source bytes before success, retains already-applied profile/history as documented.

Deferred retry repair: F's committed uncertain editor lock is included through A
fa1130. Backend regression simulates response loss AFTER actual correction commit:
exact retry returns the same result/version, changed text with same key409, and
only one correction revision exists. User-visible editor consistency is F's repair;
D does not edit F files or call backend idempotency a frontend fix.

Profile save now accepts A-approved onboarding metadata, merges omitted nested
fields without deleting existing input, validates stage/objective/enrichment bounds,
and leaves skill evidence/selected plan untouched. This supports F's approved UI:
stage,objective,context,education_level,institution,interests,work_areas,
optional_enrichment. Canonical evidence/preferences keep their existing scale/source
semantics; self-reported onboarding does not certify competence or change scoring.

Checks: focused profile/library/storage tests include actual pypdf6.21.2 extraction
from a synthetic text PDF, blank/scanned, encrypted and page-limit cases; no automatic
profile write; parser concurrent write and deletion race; CV purpose/legacy behavior;
onboarding merge/invalid enum; response-loss retry/no duplicate correction. pypdf
was installed into ignored ml/artifacts/session-d/product/python-deps for D tests,
not the shared read-only Python environment. Production installs A's dependency.

Reproduce focused local tests:
```sh
source .env.local
PYTHONPATH=ml/artifacts/session-d/product/python-deps:ml/src:apps/backend-api:apps/backend-api/tests "$MINDER_PYTHON" -m unittest test_profiles test_documents test_document_storage
```
Without that extra dependency directory PDF support honestly reports unavailable;
the normal environment was not silently modified. No files/extracted private text,
secrets or real-user fixtures were committed. All test documents are synthetic.

Integrated suite:121 discovered,117 passed/4 Clerk SDK skips on legacy3.9;
actual pypdf tests were enabled and passed, not skipped. Loopback concurrency
checks ran with required sandbox permission. No live provider/hosted acceptance.
