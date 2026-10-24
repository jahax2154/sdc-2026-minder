# MA2 owner request — concrete structured proposal review

F ownership only; A does not edit frontend. Current combined backend147tests and
4deploy checks pass. A discovered one newly exposed UI contract gap while reviewing
MA1-R06/R08 structured tools against actual F diffLabel:

ui.js diffLabel uses esc(d.after) / esc(d.before). New create_task after is a typed
Task object and automation scope before/after is {plan_ids:[...]}; String(object)
shows [object Object]. Pending proposal approval must not conceal the concrete task/
scope. Please F commit MF3-R01 (or named refinement): render structured before/after
reviewably (friendly typed task fields/scope + complete escaped details as needed),
no model HTML, preserve exact proposal hash/version approve/reject controls, phone
width. Test an actual backend create_task proposal, zero state effects until exact
approval/rejection; don't substitute a mocked approval result.

Also hide unsupported generic Undo for create_task/schedule_task/configure_automation;
use canonical task/daily controls. A intentionally rejects guessed inverse creation/
scheduling (new task cancel, schedule edit, automation pause/cancel are explicit).
Existing completion uses its task Undo control, profile preference/reset and ordinary
scalar task edits retain exact supported reversals. A is repairing optional goal/text
field removal on exact undo independently; no F backend edits.

This request follows real source inspection, not an assumed whole-page failure.
All approved pages/chat/history/CV acceptance evidence remains preserved. F should
send a focused committed handoff; A integrates without copying ongoing files.
