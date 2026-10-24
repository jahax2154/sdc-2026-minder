# A-UX3-R01 — newest dated Home notice, missing dates preserved

F UX3/4/5 commitsc7ff863bcfae8f5c8f45a4e4ea4bf1c24ec87550,
140d8affc755c26909a7792f345e16135479cad5 and
efeb6d7624175dfa8ce699094f88fe5ad0f77622 integrated normally by
713d7db2a60ff3db3381a42f4c2195e510e5d509. F retains its ongoing UX6/frontend work.
This A refinement changes only its own backend read ordering, not F's files.

Actual source/integration defect: Home picks agents.notices[0] as the latest saved
update, but GET agents had no SQL date order. The owner index can return an undated
or older event first. A's actual WSGI fixture, deliberate IDs opposed to time order,
returned0-unknown/a-old/z-new; expectedz-new/a-old/0-unknown. Initial naive fixture
IDs happened to sort in time order, so were corrected before judging the regression.
Known timestamps use different UTC offsets to reject naive lexicographic sorting.

GET agents now orders by SQLite julianday(actual created_at)DESC, opaque idDESC
only as deterministic tie-break. Invalid/missing dates stay null/last, never filled
with current time. Owner boundary, response fields, event/action/schedule state,
singleton/history, ranking/model/source semantics unchanged. Read-only,0providercalls.
The same actual regression passes after the bounded change. Controlled fixture dates
are not real scheduled-event performance evidence. Failure/pass logs stay private.

F follow-up: when the selected legacy notice has no valid created_at, label it
**Your saved update**, not **latest**. Do not infer time from event ID or request
time. Current real worker notices already include created_at; legacy/fixture absence
is explicitly supported. This is a one-label bounded Home refinement owned by F.

Reproduce `checks/check_ux_notices.py` with A's existing Python3.12/PYTHONPATH.
Focused existing agent/automation/host-worker regressions:14pass0.196s. An initial
command named nonexistent test_automation; corrected to actual test_automation_state,
with no runtime defect or test relaxation. `git diff --check` passes. The
final complete backend suite belongs to final integrated acceptance. No DB migration,
source input write, paid job or hosted claim. A restarts only its own runtime after
the committed checkpoint; other processes/ongoing F work stay untouched.
