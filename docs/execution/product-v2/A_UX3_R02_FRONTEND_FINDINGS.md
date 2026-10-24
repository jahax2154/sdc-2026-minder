# A-UX3-R02 — remaining focused F-owned browser refinements

Status: **OPEN / failing integrated checks**, not frontend gate completion.
F owns all frontend files; A did not patch them. Includes final published F
739a6c3bf62775bee5729e0bd135c3e15bb15a74/codef3ea83ba490f57d96de91418a35e13319a5b55e7.
Its source changes do not contain the two narrow corrections below. Core A Home/
identity/history/progress journey passes separately; that does not waive these cases.

## F-UX3-R01 request — exhausted-page control remains visible

Actual A9111, fresh synthetic owner, one saved matching Minder conversation, real
search API returns only that row/has_morefalse/next_offsetnull. Native element
moreMinderHistory.hidden=true, but computeddisplay:flex, height38px and Playwright
isVisible=true. A class display rule overrides native hidden styling. Screenshot
and exact computed values retained privately under morning/ux-visibility/.

Please add the bounded F-owned hidden-state style for this actual control (and
inspect related sidebar hidden controls), not a backend pagination workaround.
Assert rendered invisibility after the last20+5 page, after a one-result search and
empty/no-match state. Keep Load more visible/clickable only for has_moretrue. No
model call is needed. Do not weaken the native state/actual rendered assertion.

## F-UX5-R01 request — unknown notice dates

A-UX3-R01 backend now returns dated notices by actual UTC instant, undated last.
An explicit controlled agents READ fixture with one valid saved notice lacking
created_at renders **Your latest saved update** in actual Home. The date is unknown,
so use **Your saved update** when no valid timestamp exists. Do not invent time.
This second case is a declared read-response fixture, not an actual worker/job claim.
Other backend/Home reads are real; no Profile/schedule/action write or model call.

## Reproduce and hand back

`checks/check_ux_visibility.cjs` runs both cases, captures values and intentionally
fails while either is unresolved. Browser env must omit private provider settings;
set MINDER_BROWSER_OUTPUT_DIR to A ignored namespace. Current failure evidence:
html_hiddentrue/computedflex/38px/visibletrue; undated headinglatest. Unknown-date
fixture is explicitly labelled in the report. No private screenshot/user data is
committed. Root generic collaboration messaging cannot resolve the external TUI
thread ID; this committed file is the concrete shared handoff to F.

F: preserve ongoing work, implement/test these two bounded owner changes, commit
refinements separately or together with their linked IDs, normally push your own
branch and give A full SHA. A integrates committed history and reruns this check;
no need to repeat successful real-provider calls for these CSS/label changes.
Home/sidebar full completion is held pending this exact acceptance. No main merge,
force push, framework/scoring change or deployment is requested by this handoff.
