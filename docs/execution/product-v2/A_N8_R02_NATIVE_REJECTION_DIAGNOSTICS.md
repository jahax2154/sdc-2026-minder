# A-N8-R02 — native rejected public-answer diagnostics

Actual browser regression on A f4ceba74de1723f5a76a0c28343fe48b5150e51c:
all three exact questions reached live discovery and relevant detail retrieval.
The first model call returned provider_http_error; the original adapter discarded
its upstream body. Its rejected claim and native validation rule are unavailable,
not guessed. The second received actual daily token quota limit200000,used199337,
requested1373,retry-after306.997s. The third was locally held without another
outbound call. No source-availability check is relabelled a useful-answer pass.

A's gateway now records only HTTP400 plus an allowlisted native error code in
public provider diagnostics. If the native rejection supplies parseable public
explain_public_sources arguments, the visible candidate and exact native rejection
rule are retained in that owner's existing public_web_evidence ledger. Upstream
messages, request bodies, headers, credentials and generated text never enter the
shared quota file or logs. Other tools do not capture rejected candidates. Native
rejected arguments remain rejected; no validation/approval boundary is bypassed.

The answer prompt explicitly bounds introduction/findings/advice lengths to the
existing384completion-token ceiling. The actual model is unchanged. This is a
bounded diagnosis/context refinement, not a claim that a native rejection passed.

Verification:6gateway checks0.220s and11web checks0.041s PASS using declared fixtures.
The fresh integrated PostgreSQL run also passed131tests12.730s plus actual native
server stop/start and fresh-process JSON/version refetch. Hosted checks remain open.
Full backend verification:220tests12.805s PASS,4native-PostgreSQL-specific tests
skipped in this ordinary interpreter; the separate131-check native run above passed.
