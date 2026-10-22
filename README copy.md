# Minder

**AI-assisted career exploration and personalised reskilling.**

Minder is being developed for **SDC Hackathon 2026, Domain 1: The Aiversecity Future-Ready Workforce Domain**. It aims to help a person understand their current skills, explore future roles using dated evidence, compare scenarios, and follow an actionable learning pathway with meaningful Sustainable Development Goal (SDG) connections.

The intended journey is **profile → trend evidence → ranked roles and skill gaps → scenario comparison → chosen pathway → tasks and progress**. Chat and personal agents support this journey using the same underlying information.

## Current status

This is the initial engineering documentation baseline, prepared on **20 October 2026**. The team has created a GitHub repository, but its implementation and the design mockup were not available for inspection during this update. These documents therefore distinguish intended behaviour from verified implementation.

| Item | Status |
|---|---|
| Product scope | Five product areas retained; detailed navigation awaits mockup review |
| Technology stack | Open; team discussion pending |
| Dataset, labels, model and evaluation thresholds | Open; candidates and selection criteria documented |
| Application, tests, trained artifacts and deployment | Not verified in this update |
| Replit | Intended for frontend work and integration; deployment remains a candidate |
| RunPod | Intended for GPU work when needed; no training run certified here |

**Status language:** `CONFIRMED` means a user decision or an official requirement; `PROPOSED` means a recommendation awaiting adoption; `OPEN` means unresolved. Implementation is tracked separately as planned, implemented or verified. A documented feature is not automatically implemented; verification needs actual evidence.

## Product areas

| Area | Intended experience |
|---|---|
| User Profile | Capture and edit the demonstration user's skills, experience, interests and constraints |
| LLM Chat | Explain grounded recommendations and help the user work through their choices |
| Personal Agents | Provide bounded assistance; responsibilities and triggers still need definition |
| Dashboard | Show the pathway, actionable tasks, progress, insights and relevant detail views |
| Career Explorer & Simulation | Explore trend signals, compare roles, inspect skill gaps, examine scenarios and understand SDG contributions |

The roadmap remains part of the product through the Dashboard and its detail views. The five areas are a product organisation choice; the six official capabilities and their acceptance checks are mapped in the [PRD](PRD.md#requirements-and-acceptance).

## Documentation map

| File | Owns |
|---|---|
| [PRD.md](PRD.md) | Product scope, user journeys, requirements, acceptance and competition constraints |
| [AGENTS.md](AGENTS.md) | How coding agents and teammates make and verify changes |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System boundaries, proposed repository layout, API agreement, stack and runtime decisions |
| [ML_DESIGN.md](docs/ML_DESIGN.md) | Learning task, baseline, modeling, evaluation and artifact lifecycle |
| [DATA_SOURCES.md](docs/DATA_SOURCES.md) | Source candidates, provenance, permitted use and refresh process |
| [replit.md](replit.md) | Short Replit adapter pointing to the shared rules |

This README owns project orientation, working setup instructions and delivery links. Keep detailed requirements in their owner document.

## Repository and local setup

The [proposed directory map](docs/ARCHITECTURE.md#repository-boundaries) separates frontend, API, shared career logic, offline ML work, data and submission evidence. Reconcile it with the actual repository before creating or renaming directories. The organiser's starter files do not determine the application's required file count.

**No runtime commands have been verified for this repository in this update.** After the stack is selected, replace this paragraph with tested instructions for prerequisites, dependency installation, environment variable names, synthetic data setup, development startup, relevant checks and production build/start. Provide an example configuration containing names and safe placeholders, never live credentials. Do not publish guessed commands as a working quickstart.

## Delivery links and evidence

| Item | Current entry |
|---|---|
| Team name, leader and university affiliation(s) | Pending insertion of the team's existing details |
| Member count, names, existing roles and GitHub profiles | Pending; preserve the established role assignments |
| Selected SDG track | Pending; Domain 1 is confirmed |
| Canonical GitHub repository | Pending actual URL |
| Replit project / proof of use | Pending actual project and evidence |
| Live application | Pending hosting decision and verified URL |
| Demo video and presentation | Pending final artifacts |
| RunPod evidence | Pending if used; record actual GPU/runtime/account evidence |
| Submission documents | Pending completed official forms and accessible links |

The [competition constraints](PRD.md#competition-constraints) cover public repository access, Apache 2.0, tool evidence and submission ownership. Check the actual `LICENSE` and final submission contents rather than treating this README as proof of compliance.

### Submission export checklist

Use these documents to prepare the official forms; they do not replace them. Preserve the [official submission template](https://drive.google.com/drive/folders/1Ue4zY8XBH3zpBYHFdDmVpr99gjaey-H5) requirements:

- Complete applicable fields and export one proposal PDF named `SDC2026_TeamName_Preliminary.pdf`.
- Respect the form's limits: problem context 250 words, proposed AI solution 300 words, design-thinking/deployment strategy 200 words. Internal engineering documents can be longer.
- Export the conceptual stack/system connections and sponsor-tool use from Architecture; record relevant workshop skills actually used or intended.
- Complete the [impact framework](PRD.md#impact-framework), including numerical baseline, KPI/unit, percentage improvement target and citations.
- Consolidate tool/API/service, code, dataset, pretrained-model and pre-existing-work declarations from their owner documents. The team must verify workshop completion, ownership/IP answers and the leader's declaration/signature.
- Verify setup, final links, license, required evidence and submission accessibility. Put the leader's email/phone in the required form rather than duplicating them in this public README.

Before submission, add actual challenges/learnings and future improvements supported by the work completed. Keep them distinct from current prototype scope.

## Limitations

Minder supports human career decisions. Match scores, scenario estimates and research exposure measures must not be presented as guaranteed employment outcomes. Demonstrations use synthetic profiles, and recommendations must identify their supporting sources. Until measured, neither model quality nor uninterrupted agent operation is a product claim.

The project brief and preliminary-round expectations are defined in the [official Domain 1 brief, §§3–8](https://drive.google.com/file/d/1x6Nvjl_1Gc-v3SsTnf44HVEJZQsbWVRA/view).
