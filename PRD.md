# Minder — Product requirements

**Status:** Initial working baseline, 20 October 2026. Status terms are defined in [README](README.md#current-status). This document owns scope and acceptance; design choices belong in [Architecture](docs/ARCHITECTURE.md).

## Product goal and user

Help a person move from their current skills to an evidence-informed future role and a practical reskilling pathway. Make the source, uncertainty and SDG contribution of recommendations understandable.

**CONFIRMED:** retain the five product areas below and focus engineering on the first prototype. **OPEN:** the initial target persona, geography, role catalogue size, planning horizon, supported languages and detailed mockup. The domain identifies working adults, graduates/career switchers, HR teams and education advisers as possible audiences; it does not require the team to build every audience's workflow. Choose one primary demonstration user before tailoring features. [Domain brief, §§2–3](https://drive.google.com/file/d/1x6Nvjl_1Gc-v3SsTnf44HVEJZQsbWVRA/view).

## First-prototype scope

| ID / area | Required product intent | Detail still open |
|---|---|---|
| F01 User Profile | Enter and revise a synthetic profile containing relevant skills, experience and interests; make missing inputs explicit | Input form and validation; upload support is optional |
| F02 LLM Chat | Discuss the same evidence, roles, gaps and pathway used elsewhere; identify the LLM and cite recommendations | Provider/model, conversation storage and exact supported actions |
| F03 Personal Agents | Present useful, bounded assistance with visible inputs, action status and results | Responsibilities, triggers, allowed tools and run limits |
| F04 Dashboard | Show the selected pathway/roadmap, ordered tasks, progress, relevant insights and detail views | Mockup layout, progress events and persistence behaviour |
| F05 Career Explorer & Simulation | Show dated signals, ranked roles, match explanations, skill gaps, SDG links and multiple scenarios | Navigation/grouping and scenario assumptions |

The five areas are retained in the product baseline; their navigation and implementation depth remain subject to the mockup review. The roadmap is included under F04 rather than removed. Trend processing, matching, persistence and SDG mapping serve multiple areas.

**PROPOSED first integration slice:** synthetic profile → one refreshable evidence source → explained role ranking → chosen pathway, with the same recommendation run visible to Chat and Dashboard. Implement the other retained areas in bounded increments; this slice does not delete them from the product.

**PROPOSED agent behaviour:** an on-demand review can propose a pathway change for the user to accept. Scheduled or continuous operation requires a separate runtime decision and evidence. “24/7” remains an aspiration, not an initial availability claim. Progress completion records activity; it does not automatically certify skill mastery or retrain the model.

## Primary user journey

1. Load or edit a clearly fictional profile; see any missing information before matching.
2. Inspect source dates and available trend evidence, including stale or unavailable data.
3. Compare ranked roles, explanations, gaps and scenario assumptions. Different scenarios may legitimately produce the same ranking.
4. Choose a role and receive ordered learning steps with estimated effort, real resource links and SDG explanations.
5. Review tasks and progress in Dashboard; ask Chat to explain the current recommendation. Any agent proposal is distinguishable from a user-accepted plan.

## Requirements and acceptance

The capabilities below are **official requirements** from the [Domain 1 brief, §4](https://drive.google.com/file/d/1x6Nvjl_1Gc-v3SsTnf44HVEJZQsbWVRA/view). The checks are the proposed team's operational interpretation, not additional organiser wording.

| ID | Capability / placement | Acceptance evidence |
|---|---|---|
| D1-01 | Profile intake — F01 | A synthetic profile with skills, experience and interests reaches matching. Invalid or missing data is handled visibly. A form or questionnaire can satisfy this without CV parsing. |
| D1-02 | Updatable AI/job-market source — F05, F04 | An identifiable source has a working refresh/import procedure. Display source and relevant date. A controlled evidence change produces a justified, traceable downstream change; hardcoded lists alone fail. |
| D1-03 | Explained future-role ranking — F05 | Real, sourced roles have match scores with stated meaning, explanations and skill gaps. Known input changes affect relevant results; identical versioned inputs are reproducible subject to documented nondeterminism. |
| D1-04 | Personalised pathway — F04 | A selected role produces ordered steps addressing gaps, estimated time and verified free/low-cost resources. Separate estimates from measured outcomes. |
| D1-05 | SDG contribution — F05, F04 | Every recommended role and skill maps to at least one SDG with a defensible contribution explanation. Decorative badges alone fail; using all 17 goals is not required. |
| D1-06 | Uncertainty — F05 | At least two scenarios show their assumptions and implications. Predictions are visibly estimates; do not force artificial differences when evidence supports stability. |

**Milestone distinction:** the final product must cover all six. The preliminary proposal explains all six, while its working demo may focus on its most important feature, usually trends feeding matching. The team's five-area vision and engineering goals are broader than that preliminary minimum. [Domain brief, §§4, 8](https://drive.google.com/file/d/1x6Nvjl_1Gc-v3SsTnf44HVEJZQsbWVRA/view).

## Experience and engineering acceptance

All relevant screens need loading, empty, invalid-input and service-error states. Stale evidence and unavailable models must be visible. Temporary fixtures must be labelled; a mock-backed screen does not prove backend integration.

The integrated prototype should keep profile, recommendation, scenario, model/source versions and selected pathway consistent across screens. If shared hosting retains sessions, one user's state must not appear in another's; identity/session mechanism remains open. Performance targets must be selected for the actual demo environment and then measured, rather than assumed.

| Gate | Evidence needed | Status in this update |
|---|---|---|
| G1 Scope and interface | Primary persona, mockup coverage, stack decision and agreed frontend/backend contract | Pending |
| G2 Data and matching | Permitted source snapshot, refresh path, baseline, explained ranking and evaluation design | Pending |
| G3 Integrated journey | Real UI/API/state flow, appropriate failure handling, pathway and scenario checks; relevant tests recorded | Not verified |
| G4 Demonstration readiness | Reproducible setup, selected hosting checked, truthful limitations, working evidence links and submission artifacts | Not verified |

These are review criteria, not a requirement to ask permission before routine work. Continue authorised work while resolving the specific decisions that affect it. A trained model is not automatically necessary to demonstrate an honest baseline, and baseline behaviour must be labelled.

## Impact framework

The official proposal asks for exact SDG sub-targets, a numerical starting baseline, a measurable KPI with a unit, and a realistic percentage improvement target for Phase 2. Estimates may use cited research or public benchmarks; they must be identified as estimates. [Preliminary proposal template, §4](https://drive.google.com/drive/folders/1Ue4zY8XBH3zpBYHFdDmVpr99gjaey-H5).

| Field | Initial baseline |
|---|---|
| Selected SDG track and sub-target(s) | OPEN; assess the Domain 1 brief's targets 4.3, 4.4, 8.2 and 8.5 against the selected user/outcome |
| Core KPI and unit | PROPOSED: time to produce a source-supported, rubric-acceptable reskilling plan, in minutes per synthetic profile |
| Current numerical baseline | OPEN; measure the comparison workflow or cite a defensible benchmark |
| Phase 2 improvement target | OPEN; select a percentage after baseline and feasibility review |
| Evaluation conditions | OPEN; define comparison workflow, shared cases, quality rubric, sample count and measurement method |

For a lower-is-better time KPI with a positive baseline, improvement is `(baseline − assisted time) / baseline × 100%`. Hold plan quality constant; a fast but unsupported plan is not an improvement. This proposed KPI measures assistance efficiency, not employment gains or proven SDG impact. Keep broader contribution claims separate and supported. No baseline, target or result has been measured by this documentation work.

## Competition constraints

This section owns the shared competition rules; other documents link here.

- **Data and AI:** use public, open or synthetic data; no real personal data or real CVs. Disclose the language model used. Cite every recommendation and invent no jobs, courses or statistics. Support human decisions; do not make final hiring decisions. Full course creation, payments and real recruitment integrations are out of scope. [Domain brief, §6](https://drive.google.com/file/d/1x6Nvjl_1Gc-v3SsTnf44HVEJZQsbWVRA/view).
- **Tools:** include Replit in the solution. Work needing a GPU, including training, fine-tuning or inference, must use RunPod; CPU-only work can run elsewhere. Replit hosting is not mandatory: an eligible project/history link can demonstrate use. [Participant Handbook, §§9.3–9.4, 10.6](https://drive.google.com/file/d/1fGBS-jevDj_FrF8wsbYNPzyU5TTrfk1V/view).
- **Repository and evidence:** provide a public repository accessible throughout judging and an Apache 2.0 `LICENSE`, preserving applicable copyright. Complete the Technical & Tools Declaration with actual Replit evidence; if RunPod was used, include the required account/dashboard evidence, GPU type, runtime and Pod ID or serverless endpoint. [Participant Handbook, §§10.2–10.7](https://drive.google.com/file/d/1fGBS-jevDj_FrF8wsbYNPzyU5TTrfk1V/view).
- **Ownership and history:** the team leader submits final deliverables; repository ownership is not assigned to a particular role in the reviewed rules. Maintain truthful, traceable work history and observe the competition's repository timing and submission cutoff. [Official Handbook, §4.2.9](https://drive.google.com/file/d/1vDGxSLufFrE9h6T8-KY1ltxmAgQln23k/view); [Terms & Conditions, §§5.5, 6.6](https://drive.google.com/file/d/1tZOLKK-fA7Uh3zu1otdL6Z-oC_FKMtyl/view).

## Mockup review and open decisions

The mockup has not been reviewed here. When available, record findings in this section or the relevant implementation issue: map every F01–F05 area and D1-01–D1-06 capability to a screen, check the end-to-end journey, source/uncertainty visibility, pathway detail, error states and real API dependencies. Identify missing behaviour before expanding scope.

| Decision | Current state | Next evidence |
|---|---|---|
| Primary user and market | OPEN | Team's chosen demonstration persona and supported data coverage |
| Navigation and feature depth | OPEN | Actual mockup and feature coverage review |
| Chat and agent actions | OPEN | Concrete useful action, authority, limits and failure behaviour |
| Scenario assumptions and horizon | OPEN | Defensible source-based assumptions and product explanation |
| Resource/time estimates | OPEN | Reviewed resource catalogue and explicit effort assumptions |
| Model and deployment choices | OPEN | Decisions in Architecture, ML Design and Data Sources |
