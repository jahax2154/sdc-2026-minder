# Minder V1 — package-level approval summary

Prepared 21 October 2026. Status: proposed for your review. The full specification
is in `MINDER_POLICY_REVIEW_v1.md`; exact repo files are in `repo_overlay/`.
This summary is a reading aid, not a second editable policy authority.

## What this package changes

Approve shared definitions and rules once. Codex then implements them, accepts
routine source-backed records through automatic checks, and reports exceptions.
You do not sign every role, mapping, industry slice or quarterly release. Human
work concentrates on unresolved semantic decisions and a small blind calibration
set. Automatic acceptance stays distinguishable from human review.

## Decisions covered by approval

| Area | V1 definition or rule |
| --- | --- |
| Target | Suitability of a role's initial preparation milestone for this user within a stated horizon; no hiring probability or full-career certification |
| Profile | Skills/evidence, interests, projects/achievements, education/experience, learning time, work preferences/constraints, target market, resources/budget and career goal |
| Existing features | C skill coverage; I interests; T time feasibility; R resources; W work style |
| Existing baseline | F=100×(0.40C+0.20I+0.20T+0.10R+0.10W), with all five components in [0,1] |
| Horizon/effort | Default 12 weeks; T=min(1,h×H/E), T=1 for known E=0; use the upper bound of an accepted effort range |
| Evidence | All positive-weight milestone criteria assessed, Q=1, and all features known before issuing F; otherwise show known components and targeted missing-information reasons |
| Proposed utility anchors | Criteria/interests/work style use explicit 0/0.5/1 anchors; resource groups use 0/1; unanswered never means neutral or absent |
| Routine weights | Required milestone criteria, interest tags, resource groups and soft work-preference tags default to equal weight 1; named policy overrides remain traceable; no per-role coefficient approval |
| Occupation data | Import pinned source definitions/skills; validate IDs, versions, mappings, evidence and milestone derivations; avoid manual reconstruction of every occupation |
| Proposed market index | D=100×(0.60×demand-share percentile+0.40×YoY-growth percentile), within a frozen compatible cohort; minimum five entities |
| Index interpretation | Relative observed demand/activity in the stated source population; separate role, industry, skill and employer cohorts; raw values and source scope remain visible |
| Existing combination | S=0.70F+0.30D only when every ranked role has compatible market evidence; otherwise rank the whole set by F |
| Independent labels | 0 weak, 1 plausible, 2 strong preparation relevance; assign without seeing model scores; generated labels are provisional or policy-distillation targets |
| Learners | Keep existing baseline/Ridge/CPU XGBoost architecture; default baseline until independent evaluation and conformance justify a change |
| Pathway | Valid prerequisite graph, verified resource alternatives, time/cost basis, capacity-respecting schedule and explicit gaps; no guaranteed mastery |
| Scenarios | Moderate/faster AI-adoption assumptions plus deterministic what-if calculations; no invented forecast effects or unsupported market multipliers |
| SDGs | Explain relevant target links for each served role/skill; do not attach all 17 arbitrarily or claim measured social impact |
| Demo data | Public/open/synthetic data and synthetic profiles as required by the supplied brief |

The baseline is an inherited product policy, not a proven optimal equation. The
60/40 market index, five-entity guard and utility anchors are proposed defaults,
not statistical discoveries. Large source volume does not validate them.

## What each data family contributes

- Occupational references and crosswalks define work and compatible identifiers.
- Market observations support measured demand and comparisons within their scope.
- Synthetic profiles exercise intake, features and the user journey.
- Independent user–role judgments train/evaluate personal-fit agreement.
- Verified learning resources and task templates support the preparation pathway.
- AI signals support dated scenario reasoning; progress events update user state.

Do not combine these into one undifferentiated training dataset. The reported
952 market rows are not 952 independently labeled personal-fit cases. Skill and
employer demand remain unsupported until suitable observations are acquired.
The concrete real-world factor/source coverage is the next assessment; this
package defines how to assess it without pretending it is already sufficient.

## Chat and agent scope

Use one shared Groq adapter, initially `openai/gpt-oss-20b`. Backend scores,
sources and saved state remain authoritative. Validate structured replies,
evidence IDs, ownership, versions and proposed actions. Chat can start now
against the existing result interface without waiting for new model training.

Proposed chat budgets: 20-second request timeout, 45-second total deadline,
one transient retry, one schema-repair attempt within that deadline,
1500 output tokens and server concurrency two. These are application settings,
not promised provider quotas or measured performance.

Career Progress Coach reacts to a progress event or scheduled check, loads
bounded context, checks prerequisites and saves a next-action suggestion. It
does not autonomously select careers, replace plans, certify mastery or contact
others. Run limits: four tool invocations, two LLM requests and 60 seconds,
including retries. Duplicate/stale events cannot create conflicting proposals.
Claim unattended operation only after an observed deployed scheduled run.

## Execution gates

1. **G1 — Policy integration:** compile this package into the existing pipeline,
   automatically validate role/milestone data, and return traceable synthetic
   comparisons plus one exception report.
2. **G2 — Grounded chat, immediate:** wire saved results to Groq and the chat UI;
   verify failures and grounding. Can proceed independently of G1 activation/G3.
3. **G3 — Coverage and learning:** materialize the factor/source coverage report,
   compute supported market indexes, and run bounded empirical comparisons when
   independent labels exist. Tiny pilots remain exploratory.
4. **G4 — Bounded coach:** connect a progress event to a saved suggestion and UI;
   verify scheduling separately in deployment.

Each task starts with the required output and uses the shortest correct path.
Codex owns routine implementation, validation, imports and reports. Preserve one
policy source and the actual repository architecture. No repeated per-record
approval loops, speculative frameworks or open-ended source gathering.

New data refreshes affected observations/features/indexes. Changed feature
meanings, targets or independently labeled data can require retraining the
affected estimator; they do not require rebuilding the application. No rule
promises that a trained model will never need refitting.

Approval covers the documented definitions, proposed defaults and automated
workflow. It does not manufacture source correctness, gold labels, measured
career accuracy, live API execution or deployment evidence. Record the actual
package approval against its version/hash; retain the original pending records
and previous gate reports as history.
