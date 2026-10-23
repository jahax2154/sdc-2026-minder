# F-R1 — Context and request lifecycle

Status: passed targeted browser fixtures; final real integrated chat depends on A's
response contract/routing repair. Baseline0a876d2748ed33c05dbabe9f0a11c7d20b52e739.
No backend/provider/grounder/scoring edits. Existing API shape retained for now.

Context starts closed, has Close and aria-expanded toggle, preserves open/closed
intent across incoming replies and draft/scroll/layout on close. Desktop is nonmodal;
<=1050px overlay has dialog semantics, background inert, focus cycle/Escape return.
Working… is primary pending copy. Explicit Stop waiting aborts browser wait and warns
server processing may finish. Success/error/cancel/deadline all terminate pending;
duplicate submission blocked. Question remains recoverable for manual review/resend.
Actual validated content precedes provider diagnostics; relevant limitations remain
visible, extra limitations expandable, attached sources retained. No canned answer.

Client deadlines include body reads: ordinary reads12s, writes30s, chat90s. Baseline
ordinary reads1-10ms; chat16s, concurrent profile GET16.5s. These conservative local
recovery bounds are not expected-duration or production-SLA claims. No automatic
write/chat retry. F-R3 will make saved sections independent; A handles server blocking.

Checks: tests/repair_ui.cjs (explicit intercept fixtures, zero provider) passed Context
mouse/Close/Escape/mobile focus, width+draft+scroll retention, no reopening on response,
Working success/failure/cancellation/timeout clearing and duplicate prevention. Chat
90s deadline compressed to80ms by test-only browser timer shim. F-R1-fixtures.json
is sanitized result. Node client/minder syntax and git diff checks passed. Screenshot
/private/tmp/minder-f-repair-context-mobile.png supplied; final real screenshots follow.
