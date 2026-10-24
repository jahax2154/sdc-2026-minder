# MF3-R01 — concrete structured proposal review

Addresses A449531c owner request; dependency A37d9fcb (includes canonical action/
automation contracts and supported Undo boundaries). F remains frontend-only owner.

Structured diffs now display readable task title/description/state/schedule/effort/
prerequisites, explicit all-own-plans vs selected plan scope, and complete escaped
JSON details. Scalar and array values remain concrete. Proposal preview hash,
expected revision and exact approve/reject body are unchanged. No model HTML.
Unsupported generic Undo is hidden for create_task/schedule_task/configure_automation;
completion retains canonical task Undo. Supported scalar reversals remain available.

Created activity review loads CURRENT canonical plan/task, then exposes explicit
edit, feasible schedule and cancel controls inside Mindbot (also on My Path task
view). Each uses actual product/task-action with version/key; uncertain changes lock
until exact retry or saved-state reload. No guessed inverse creation. Automation
approval refreshes actual daily settings so scope is immediately consistent.

Actual morning_structured_proposals.cjs passed on F local runtime/A37d9fcb:
real create_task proposals make zero target/version effects before decision;
rejection preserves version; exact approval creates one task. Friendly values/full
escaped JSON fit390px viewport. Malicious-looking synthetic task title stays inert.
Canonical edit/explicit scheduling/cancel remain inside Mindbot and persist. Actual
configure_automation scope proposal preserves settings until approval, then daily UI
shows the owned selected plan. Unsupported Undo remains hidden. No page errors.
No provider/model result was mocked; these tests exercise actual backend proposals,
executor, canonical task state and daily writer. They make no model-generation claim.

Related tested recovery: an approval response deliberately lost AFTER real commit
requires reload of saved proposals, reconciles actual applied state, and makes one
request/one action record. The welcome/history race and nested scroll-owner issue
were repaired so independently loaded action controls remain reachable.

UI http://127.0.0.1:9106/#mindbots. Screenshot:
/private/tmp/minder-f-morning-structured/typed-task-review-mobile.png (the title is
an explicitly malicious-content software fixture, rendered as inert text).
Evidence adjacent. No backend/provider/policy edits by F and no deployment.
