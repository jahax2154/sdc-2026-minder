# MA1-C01-R02 — reconcile actual MD2 document export

Integrated D ab0a8f852171553074c990e80e6722e6b75af656. Shared schema now matches its
actual CV purpose_basis and legacy_unclassified metadata, private-volume mode with
mount_verified_restart_pending (still durable_hosting_verified:false), bounded text
PDF support fields and explicit extraction unavailable reasons. Retain earlier
unclassified enum for compatibility, never convert a legacy record automatically.

Actual synthetic local-development library list/upload/extract/download/delete DTOs
validated against exact shared schema via checks/check_document_contracts.py. First
harness delete omitted expected_version and was rejected correctly; corrected it to
use the actual post-extraction version. No service assertion or guard weakened.
This is real local file/DB behavior, not hosted volume, live login or PDF support in
an interpreter without pypdf. D owns parser/security/review; F owns visible retry.
