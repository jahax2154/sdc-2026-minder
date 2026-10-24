# A-N8-R03 — remove duplicated public evidence context

The public-answer request previously sent each passage and then its quoted text
again, plus repeated canonical source IDs/hashes. The compact context now contains
short server-assigned references, actual source dates/geography/scope and question-
selected passage keys. The model returns only a passage key; the server retains
its existing exact quote/source mapping, complete private evidence ledger and all
claim checks. Raw URLs and canonical IDs are absent from model context. Full URLs
remain server-owned in the user-visible citations. No profile/history is added.

Measured on the same actual official monthly source: context JSON1363→702characters.
This is a character measurement, not a native token saving or provider-success
claim. All12focused web tests PASS0.045s, including correct mapping when a short
unquotable heading precedes the first supporting line. The active policies and
public response shape are retained; no provider model or billing change.
