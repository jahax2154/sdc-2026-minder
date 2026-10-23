# A bounded owner refinement requests

## F-DOC-REVIEW-R01 — visible review intent after an uncertain response

Code-review finding at F6f3fa4035cc0724a1e49e9351a59a95560fcfdae, not reproduced
by A's happy-path browser acceptance. Owner: F, pages/documents.js applyDocument.

The handler freezes `exactBody ??=` on first submit. On an unconfirmed error the
textarea stays editable; a subsequent save reuses that earlier body even if its
displayed text changed. After a response loss following a real commit, the backend
correctly returns the first exact receipt, while the current form may show a newer
intent. The frontend must not present that newer text as the request being saved.

Please make the pending/retry scope explicit: lock the reviewed text while its
exact request is uncertain, or reconcile the original outcome/current profile
before enabling a genuinely new edited intent with a fresh key/version. Keep
idempotent uncertain retry; do not blindly generate another key or automatically
apply changed text. A clear refresh/review path may discard the uncertain editor.
The owner chooses the small implementation; no new product decision is required.

Add a bounded fault-injection check for a response lost after actual correction
commit, then an attempted text edit/retry. Label that as a simulated transport
failure; assert only one original mutation and no mismatch between displayed
confirmed intent and transmitted payload. Also preserve exact retry and normal
explicit review/no-mastery checks. No shared/backend/schema changes needed.

All ordinary A document lifecycle/default-disabled checks passed at P1.5. This
request does not claim a real provider/storage incident or invalidate those
recorded cases. Return a focused committed F refinement; A will integrate it.
