# A-FG1 — source display and saved-career read contract

Status: backend bounded implementation; frontend and combined acceptance open.
Base A5384b90a24b0cf23dfe55e1535ae4dca38b55dcd, F739a6c3bf62775bee5729e0bd135c3e15bb15a74
already integrated. F remains exclusive frontend writer. D persistence, E read
adapters and actual scorer remain unchanged. Integrate committed slices only.

Verification: six focused real-source API regressions pass; full backend suite
168pass,0skip,7.875s. The first sandboxed full run could not bind three loopback
test servers; rerun with authorized loopback access passed. No browser completion
is inferred from those checks. Evidence logs remain private under
`ml/artifacts/session-a/product/morning/functional-backend-fg1*.log`.

## Available to F now

`POST /api/role-requirements` returns the existing unchanged `role`, plus
`role_selection: {role_id, source: request | saved_direction}` and `display`,
validated by `contracts/role-display.v1.schema.json`.

- Omit `role_id` to read the authenticated user's persisted direction. Explicit
  null/blank/non-string fails422; an unknown explicit ID fails404. Missing saved
  direction fails422 `career_selection_required`. Reading another role is not a
  direction write. Global match requests still consider all eligible roles.
- `display.skills[]`: source-backed `label`, `subject_id`, `label_status`,
  `label_source`; `measurements[]` includes original `evidence_id`, `unit`, raw
  `value`, `availability`, plain-language `label`/`explanation` and full `source`.
  Reading Comprehension for Software Developers has importance3.5 and activity
  level4.25. They are different measures: nineteen records group into ten skills,
  with all nineteen retained. No averaging, deletion or inferred mastery.
- `personal_evidence` is separate: status `not_assessed`, `recorded_unassessed`,
  `anchored_evidence_recorded` or `needs_clarification`; record/anchor counts,
  evidence IDs, assessment kinds and an explanation. Saved notes or occupation
  ratings are not the user's competence. Contradictory anchored evidence needs
  clarification. Private statements are not copied into this display DTO.
- Ten of ten current requirement subjects across1016 catalogue roles have pinned
  O*NET anchor labels. No LLM label invention or dependence on the first fifty
  search results. Unknown future labels remain explicitly unavailable. Values
  are source-native: do not add unverified scale denominators or percentages.

`POST /api/role-evidence` has the same optional-role resolution and unchanged
current `records`/`passages`/policy. It adds `forecast: MarketResult | null` and
`forecast_error: null | forecast_service_unavailable | forecast_read_failed`.
MarketResult is the existing typed contract, with kind=forecast, entity_type=role,
matching entity_id, source dates, target_period, status/value/missing_reasons.
A valid unavailable result has error=null and value=null. A failed forecast read
never suppresses current records. No future trend, replacement probability or
rank is invented. The runtime is still local9111/8111, not a hosted teammate URL.

## F implementation requested by the current gate

1. Render sourced grouped skill names and distinct importance/activity values in
   Compare, role details and My Path Skills. Show occupational measurements and
   personal evidence separately. Preserve source/geography/date and unknowns.
   Return role.label is authoritative even outside the first50 catalogue page.
2. Reconcile saved direction with browsing/compare state. Matches selection,
   Compare, Outlook and My Path must retain the saved choice across navigation
   and refresh. A temporary open/compare role must not erase the saved choice.
   Use omitted-ID scoped reads when no explicit view role is present. Ensure the
   selected option exists even when not in the first50 search results.
3. Consume the actual forecast status rather than a permanent sentence claiming
   no forecast contract. Explain current evidence and unavailable future evidence
   separately, with dates and measurement scope. Replace raw engineering copy.
4. All four My Path tabs read the same accepted active plan; Next selects an
   eligible activity, Roadmap groups its saved stages, Skills shows sourced needs
   and personal evidence, Progress shows actual task activity. Complete updates
   progress without generation/replacement. Reconcile Home/Next task choice with
   the canonical overview adapter if their order can diverge.
5. Finish existing F-UX3-R01 hidden Load-more and F-UX5-R01 undated-notice copy;
   reproductions remain in A_UX3_R02_FRONTEND_FINDINGS.md. No waiver.
6. Audit the smaller display surfaces too: current Home Skills uses the first
   evidence.subject_id/value directly, savedPlan prints selected_role_id, and
   dailyAutomation labels plan checkboxes with selected_role_id. Hydrate sourced
   occupational/skill labels there as well; retain explicit user text where it
   is an actual user-defined label, without treating its value as competence.

## A first fresh-browser result (backend0a39b39 / old F code)

`A_FUNCTIONAL_GATE_AUDIT.md` records actual handler/API/state connections, passes,
failures and owners. Three source anchored assessments were entered through UI,
not a Profile fixture.910 personally assessed,5 comparable current ranks,900
strictly personal-only;7 shortage contexts,0 exact-role shortage,907 sector
contexts. Actual Qwen roadmap:3stages/3tasks, native provider1686.540ms, complete
generation/save/activation2127ms. Explicit save then separate activation passed;
completion0/3→1/3 persisted without replacing roadmap or generating again.
Compare after a single-result search was empty; Skills raw repeated IDs failed.
The CV attempt used an incorrect test route and is not a product failure claim;
corrected final journey must exercise Profile→My Record→CV files. Browser
session credentials must not be exported to a file to retain test continuity.

Return exact tested commit SHA(s), handler/route changes and actual browser
evidence. A will integrate ancestry-preservingly and run the combined fresh
onboarding journey. Do not change A runtime/DB or backend files. No new model,
scoring policy, migration, main merge or deployment is required for this slice.

## Gate proof required

Fresh anonymous initial onboarding through UI (no pre-completed profile/plan),
focused minimum missing evidence, actual matching coverage, role choice, Compare/
Outlook refresh/navigation, actual Qwen roadmap draft, explicit acceptance and
activation, four distinct tabs on that plan and completion/progress without model
regeneration. Also audit visible Home, CV, history/chat, Mindbot actions/scheduling.
Classify browser/real-provider/fixture checks separately and preserve initial
failures. Missing implementation remains an owned open item until repaired.
