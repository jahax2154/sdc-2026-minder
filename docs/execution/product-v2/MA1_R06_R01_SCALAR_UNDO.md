# MA1-R06-R01 — exact optional-text reversal

Common action preview now removes an optional goal/title/description when exact
Undo restores its originally absent value, rather than writing invalid null text.
Expected version, exact before/after diff, authority/idempotency/audit and locked/
completed protections remain. Preference reset still removes its prior effect.
Generic undo of task creation/scheduling or daily automation remains explicitly
unsupported: use the canonical task or daily pause/cancel controls. F owns hiding
those misleading Undo buttons under MA2_FRONTEND_REFINEMENTS.md. No history rewrite,
implicit delete, new scoring semantics or duplicate action mechanism.
