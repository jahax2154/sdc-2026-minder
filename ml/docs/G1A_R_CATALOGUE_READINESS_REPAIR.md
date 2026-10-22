# G1A-R — repair catalogue readiness from actual failure reasons

Copy this entire prompt into the existing ML engineering Codex session.

```text
GATE G1A-R — CATALOGUE READINESS REPAIR

Execute this focused repair gate in the existing Minder repository. G1A code
implementation passed, but catalogue readiness is partial and the latest report
contains 18 unscored pairs. A separate session is implementing Groq chat. Finish
all authorized unblocked repairs, run relevant checks, and stop after the report.

READ FIRST
- Applicable AGENTS.md and actual repository conventions.
- ml/docs/MINDER_POLICY_REVIEW_v1.md and
  ml/docs/MINDER_APPROVAL_SUMMARY_v1.md, plus the actual policy configuration.
- docs/execution/gates/G1A_report.md and G1A_evidence.json.
- Actual role/milestone definitions, source records, criterion worksheets,
  profiles, mappings, feature traces and missing-input reason codes.
The summary supplied outside the repository is not sufficient to diagnose which
fields are missing. Inspect the actual evidence and service output first.

SCOPE AND OWNERSHIP
Own ML catalogue/reference/preparation data, affected feature/data adapters and
this gate's report. Preserve working G1A code, score contracts, baseline weights,
complete-evidence semantics and original pending records. Do not edit Groq/chat
modules, frontend chat files, root dependency locks or recommendation API schemas
while the parallel session works. Read shared interfaces without changing them;
use local compatible adapters if a repair truly requires one. No commit, push,
training, publishing, new spending or unrelated cleanup.

REQUIRED WORK
1. Reproduce the reported unscored results and reconcile the count of 18 with
   actual profile IDs/families, roles, milestones and any variants. Do not assume
   the old five-profile/15-pair count still describes the current input set.
2. Group failures by the UNIQUE upstream missing input, validation rule or shared
   catalogue record. Return one compact table: role/milestone, missing field,
   affected-pair count, provenance, source availability and proposed repair.
   Distinguish missing role definitions, missing user evidence, unsupported
   mappings, code/schema defects and genuinely undecided product assumptions.
   Independent target labels are not prerequisites for baseline inference.
3. Resolve deterministic issues automatically from existing pinned sources,
   criteria and declared policy: identifiers, mappings that can be verified,
   criterion anchors, declared equal weights, resources and trace metadata.
   Prefer source-native roles where an optional crosswalk is unavailable.
   Do not mark a mapping compatible just because its IDs exist.
4. Keep each initial preparation milestone narrow and tied to an observable
   outcome. Reuse compatible accepted task/templates and prerequisites. Full
   occupational skill lists are not automatically initial-milestone criteria.
   Do not remove essential requirements merely to force a score. If a small
   external lookup is needed, target the named missing field with primary
   sources and preserve its actual provenance; no broad scraping project.
5. Effort E must have a defensible recorded estimation basis. Reuse accepted
   estimation rules or verified resource/task durations where applicable;
   course duration is not guaranteed mastery time. Never invent hours, zero
   effort, empty resource requirements or completed assessments to clear Q=1.
   A source fact and a prototype design assumption must remain distinguishable.
6. If a field cannot be resolved without a new assumption outside the current
   policy, prepare one concrete batch of proposed milestone/template changes
   with sources, effort ranges/method, limitations and exact expected effect.
   Implement validation/loading so it is ready to apply after a real decision;
   keep unsupported assumptions inactive. Do not stop before preparing that
   reviewable result, ask for signatures on every pair, or claim the decision
   was already made. Report only the remaining decisions once.
7. Preserve existing incomplete profiles. If a complete synthetic input is needed
   for a valid role milestone, create a NEW explicitly synthetic version/case
   with anchored assessments and stated constraints. Do not claim supplied
   unknown answers were observed. Reuse the actual accepted role definitions.
8. Rerun feature building and the inference service. Aim to demonstrate at least
   one complete synthetic profile scored against each of the actual three roles
   if their catalogue evidence is adequate. Report every unresolved role/pair
   rather than forcing full readiness. Distinguish source/policy-supported role
   records from synthetic plumbing fixtures.

ACCEPTANCE AND REPORT
- A root-cause table accounts for all reproduced unscored pairs; shared repairs
  are applied once at the actual upstream source.
- The baseline vector [0.6,0.8,0.5,1,0.7] remains 67. Relevant G1A tests and changed
  catalogue/feature invariants pass. No missing values are silently imputed.
- Compare before/after eligibility, source/assumption provenance and data hashes.
  Report actual scored/unscored counts and exact remaining fields by role.
- Return callable service examples using valid real-role definitions and
  synthetic user data where possible. Empirical quality remains not_evaluated
  until independent labels exist. Do not use labels to fill missing model inputs.
- Write G1A_R_report.md and G1A_R_evidence.json under the existing gate-report
  convention. Separate implementation correctness, catalogue completeness,
  usable score coverage and independent evaluation status.

STOP AFTER THIS GATE
If catalogue evidence is ready, identify the exact versions G1B should consume.
If it is still partial, return the smallest concrete batch decision/dependency
with its affected outputs. The parallel Groq gate continues either way. No
automatic gold labels or changes to the shared recommendation contract.
```
