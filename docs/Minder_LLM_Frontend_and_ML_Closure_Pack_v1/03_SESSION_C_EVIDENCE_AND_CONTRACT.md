# Session C — evidence-type bridge and product frontend handoff

Continue from fe78c8429374d4d9748837ee9f2c94ab573c56e9.
A reports that your current grounder handles Bosch derivations but does not yet consume new
passage types. This is the specific defect to resolve; do not repeat a general privacy rewrite.

Read A's I4.7 handover and the committed I4.6 evidence/passage changes, including the current
market policy v2.1 definitions. Inspect actual interfaces before implementation.
Coordinate public contract changes with A; do not edit A-owned scoring or shared schemas concurrently.

## CL1 — export the real frontend contract early
Use 01_MINDER_MINDBOT_FRONTEND_CONTEXT.md section 2.
Write a compact endpoint/schema/example export under docs/execution/product/llm/ using actual code.
Include chat/messages, evidence, proposals, approval/rejection, action/job status and supported agent
controls. Identify the current evidence-type limitation explicitly.
Examples use fictional user data and actual source scope; no secret/private profile exports.
Tell F which revision it can wire now. Commit this bounded contract handoff.

## CL2 — support A's new passage types
Implement adapters/validators within your owned grounding boundary for the actual accepted types:
employer observations, published offerings/category proxies, related shortage-group context and
broader sector context. Respect existing semantic type definitions rather than inventing new ones.

Preserve each record's source identity, passage, dates, geography, unit, mapping direction/scope and
qualification. Specific requirements:
- A category proxy cannot become a narrow-role national count.
- Related MyCOL group/membership evidence cannot become exact whole-role shortage designation.
- Sector context cannot become an individual role's measured demand.
- Current or historical facts cannot become an available forecast.
- Synthetic/estimated values cannot inherit an official-source truth label from their anchors.
- Source unavailability or an unsupported derivation produces a safe limitation, not fabricated text.

Implement the same evidence handling for interactive chat and scheduled agent output.
Keep validated numerical values consistent with backend calculations. Preserve safe output rejection,
payload minimization, logs and action authority.
No general-law runtime browsing and no automatic legal-compliance claim.
Commit CL2 with focused regression evidence.

## CL3 — real provider and handoff
With the existing working C secret configuration, exercise representative real-provider responses
for the new passage types. Verify actual supporting meaning, not merely source-link existence.
Cover quantity/date/scope mismatch, non-Bosch valid output, rejected overstatement, unavailable
forecast, direct action and proactive proposal boundaries. Reuse unchanged tests where sufficient.
Do not equate constrained validation with general semantic correctness.

Refresh the actual API examples/capability status after the bridge. Provide F/A full SHA, exact
changed types, schema version and test evidence.
Record any other demonstrable blocker only; do not restart completed compliance or UI work.
Commit CL3; coordinate publication through A per file 06. No independent A/B/C push race.
Remain available for F's concrete contract bugs; stop broad implementation when scope is closed.
