# A-N5 — integrate E's committed public preview setup

A input dd843cedf335e0507441813f068625592d7808fe. E exact handoff
 d6b18e3d0eb168ef1062f32e699c12e4fbbf6c8b is not already an ancestor;
its base c795 is already integrated. Merge only its missing three committed files,
preserving both histories. No other lane's directory or uncommitted work is staged.

Reviewed deploy/operator.py, deploy/test_operator.py and E/ME4_PRIVATE_SETUP.md.
The helper derives public preview issuer/JWKS from an actual publishable key,
validates the exact Clerk host, and preserves existing private config fields. It
needs no server secret for public JWKS discovery; online session verification still
needs valid server access. No fake login, bypass, deployment, main merge or billing
change is introduced.10deploy tests pass0.128s (next-e-merged-tests.log).

This is setup integration, not hosted acceptance or authorization to declare the
new product gate complete. No hosted URL/deployed SHA is verified here. F still
has no new committed starter/proposal handoff beyond62fb94f. E should use the
committed A provider factory and shared coordination directory and avoid model
probe loops while the measured shared daily quota is near exhaustion. A's
provider-status route is a read-only inspection and consumes no model call.

Candidate semantics: starter-exploration-v1 is provisional catalogue direction,
unknown assessed competence remains unknown, public-web-answer-v1 cites actual
retrieved pages and discloses partial-source failures, all cross-chat changes
require review. The old18/18 anchored/65second gate is not this new acceptance.
Do not mark this candidate final for the judge until F's normal-intake browser
journey and the live once-only approval check have passing evidence.
