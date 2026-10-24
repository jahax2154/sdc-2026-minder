# ME10 — identify the published data failure

Approved source: 001ce14af14069a2783ee39eaae44f8239381bb5.
Actual failed publication: 4af9e8b2-a6f0-4870-83b9-4a4a6d08b1de.
First fatal: runtime_data_verification_failed, 2026-10-24 22:06:11.557 UTC,
deploy/replit_bootstrap.py inventory verification guard. Reported before changes.

The published runtime reports Python 3.12.12, the explicit library bundle exists,
and its manifest, all 11 imports/pins, application imports and frontend checks
passed before this guard. The source manifest exists. BUILD emitted both the
bundle-built and runtime-verified events, including successful data verification.
Published logs expose no individual missing/mismatched artifact. Replit confirms
published-runtime shell/file inspection is unavailable. No HTTP bind occurred.

This checkpoint adds only a secret-free diagnostic before unchanged inventory
verification: for the same four approved public files, report source ID, validated
relative path, safe-path/regular-file/readable/checksum-match booleans. No payload,
credentials, arbitrary exception text, fetch, bypass or repair occurs at startup.
One controlled diagnostic publication is needed to distinguish omission from
modification. Do not infer a particular missing file from workspace contents.

13 focused tests pass, including missing, wrong bytes, valid bytes and symlink
diagnostic boundaries. No generated dependencies, raw data, private configuration
or database is committed. Existing raw/derived local inputs remain excluded and
preserved; this checkpoint does not back them up.

Public URL is still not working. No hosted authentication, two-user, saved chat,
CV, restart or scheduled-event acceptance is claimed.
