# Minder — Architecture and integration

**Status:** Proposed architecture, 20 October 2026. The existing application was not inspected. Product scope and official rules are owned by [PRD](../PRD.md); source/model details belong to [Data Sources](DATA_SOURCES.md) and [ML Design](ML_DESIGN.md).

## Boundaries and runtime

Use one canonical GitHub repository with separately owned components. Codex and Replit are development tools; code written with Codex does not require a separate “Codex runtime” or a special agent-to-agent connection. Integration happens through committed code, agreed interfaces and configured application services.

| Component | Responsibility | Must not own |
|---|---|---|
| Web application | Screens, interaction states, user input and API calls | Secret credentials, independent scoring or invented evidence |
| API/application service | Validation, session scope, orchestration, persistence and external service access | Duplicated training transformations or frontend layout |
| Career engine | Profile/role features, baseline or model scoring, gaps, scenario application and pathway rules | HTTP framework, UI or database connection management |
| Source ingestion | Retrieve/import, validate and version dated evidence | Untraceable edits to active evidence |
| Offline ML | Dataset preparation, training, evaluation and artifact export | Training during a user request |
| Storage | Versioned profile, run, pathway and progress state; artifact/snapshot references | Assumed persistence in a disposable runtime filesystem |

Recommended dependency direction: the API calls the career engine through explicit inputs/outputs; the engine receives data rather than fetching from UI or API modules. Offline ML reuses the same feature transformations. An LLM explains retrieved evidence and structured results; it does not become an unverified second ranking system.

## Repository boundaries

These paths are **PROPOSED**. Preserve an existing equivalent layout unless a change has a concrete benefit. Create directories when there is code or evidence to put in them.

| Proposed path | Contents |
|---|---|
| Root | README, PRD, AGENTS, replit.md; actual license, manifests and lockfiles as applicable |
| `docs/` | Architecture, ML Design and Data Sources |
| `apps/web/` | Frontend application |
| `apps/api/` | Backend entry points and application services |
| `packages/career-engine/` | Reusable domain and feature logic; internal package naming follows the chosen language |
| `ml/` | Offline experiment code, evaluation and small artifact manifests |
| `contracts/` | API schema/generated client types when the contract becomes executable |
| `data/` | Small permitted fixtures and source/snapshot manifests; large files stored outside Git |
| `tests/` | Cross-component integration checks; component-local tests can stay with their code |
| `submission/` | Completed official submission documents and legitimate tool evidence |

## Stack and tool decisions

| Decision | State | Rationale / next evidence |
|---|---|---|
| GitHub collaboration | CONFIRMED intent | Use the existing canonical repository, individual branches and reviewed integration |
| Codex for backend/ML engineering | CONFIRMED intent | Follow shared repository instructions; inspect actual code before implementation |
| Replit for frontend and integration | CONFIRMED intent | Import/work from the same repository and agreed API |
| React + TypeScript + Vite | PROPOSED | Evaluate against mockup, team skills and existing files; not an adopted stack |
| Python API, such as FastAPI | PROPOSED | Candidate for Python ML integration; framework choice remains open |
| Database and session/auth approach | OPEN | Decide from persistence, concurrent demo users and hosting requirements |
| Replit deployment | PROPOSED | Check runtime, persistence, resource needs and actual account budget |
| RunPod for GPU work | CONFIRMED competition constraint | Use when GPU work is needed; CPU validation can run elsewhere |

This table also seeds the tool/service declaration: intended use is not proof of actual use. For each adopted framework, API or service, record its provider/name, version or model where applicable, purpose, usage evidence, applicable terms/license and any required attribution. Record pre-existing code and ownership separately from new team work. Dataset and pretrained-model details belong in their respective owner documents.

## API contract

**Status: concrete proposal for agreement, not implemented endpoints.** Reconcile with any existing contract before adopting it. This section owns interface behaviour until an agreed machine-readable schema exists. Once generated, that schema owns exact structures; this section retains semantics and links to it. Never maintain two competing structural specifications.

### Proposed recommendation run

`POST /api/recommendation-runs` creates a run from immutable input versions. `GET /api/recommendation-runs/{run_id}` retrieves its state/result within the same authorised session. Run identity prevents screens from silently mixing different profiles or source versions.

| Request field | Proposed type | Meaning |
|---|---|---|
| `profile_version_id` | string | Existing version of the synthetic/demo profile |
| `scenario_id` | string | Existing versioned scenario definition; assumptions must be retrievable |
| `signal_snapshot_id` | string | Explicit validated evidence snapshot selected for the run |

The backend selects and records the compatible engine/model version. The request must not accept arbitrary model paths or silently replace an unavailable snapshot with unrelated data.

| Result field | Proposed type / semantics |
|---|---|
| `run_id`, `created_at` | String ID and UTC ISO 8601 timestamp |
| `status` | `pending`, `running`, `completed` or `failed`; only expose states supported by the selected execution model |
| `provenance` | Profile/scenario/snapshot versions, engine/model/feature versions, `mode` = `baseline` or `trained` |
| `data_mode` | `public`, `synthetic` or `mixed`; describe what is synthetic |
| `roles` | On completion: ordered role records with IDs, names, score, explanation, evidence references, gaps and SDG mappings |
| `warnings` | Structured issues such as stale evidence or explicitly labelled baseline fallback |

A score object identifies its name, value, scale and meaning; agree the actual scale with the scoring method. A matching index is not a calibrated hiring probability. Each gap references a known skill; each recommended role and skill carries SDG ID(s) and a contribution rationale. Evidence references resolve to publisher, source URL, relevant date, snapshot and supporting claim. Empty evidence must not be disguised as sourced output.

### Other operations and errors

| Operation | Proposed agreement needed before parallel implementation |
|---|---|
| Create/update profile | Required/optional fields, skill identifiers, validation and version behaviour |
| Browse signals/scenarios | Source dates, snapshot IDs, freshness and explicit scenario assumptions |
| Create/accept pathway | Input run and role, ordered steps, gap coverage, estimated time unit, resource references and plan version |
| Record progress | Plan/step version, event meaning and duplicate-update behaviour |
| Chat or agent run | Relevant run/plan IDs, supported action, citations, bounded execution and failure/cancellation handling |

Use a consistent error shape: `code`, user-safe `message`, optional field `details`, and a traceable request identifier. Agree mappings for invalid input, missing records, stale-version conflicts, unavailable source/model and upstream timeouts. HTTP status choices, session/auth mechanism, streaming, and synchronous versus asynchronous execution remain **OPEN**. Do not implement polling merely because possible run states are listed.

### Consistency and agent authority

Store the exact versions used by each recommendation. Dashboard, Explorer and Chat reference that run; a later refresh creates a new snapshot/run rather than silently rewriting past results. Store user acceptance separately from an agent's proposed pathway revision, and detect stale plan edits. External actions, background scheduling and autonomous retraining are not implied by the Personal Agents page.

## Replit and Codex integration

Each developer works from the canonical repository on an isolated branch/checkout. Agree the contract before parallel UI and backend integration. A frontend may temporarily use labelled contract-aligned fixtures; the integration check must call the real API. Merge coordinated changes through the team's existing review workflow and update the Replit checkout from the same repository.

If frontend and backend run together, configure the chosen development proxy/process workflow. If hosted separately, configure the actual API origin, HTTPS, server-side credentials, session handling and CORS policy where applicable. No specific command or environment variable is verified yet. Replit supports process workflows, and its root `replit.md` supplies project context to Agent. [Replit workflows](https://docs.replit.com/features/workspace-tools/workflows); [replit.md documentation](https://docs.replit.com/features/project-setup/replit-dot-md).

## Deployment decision

Replit remains a candidate until the actual application is checked. Verify build/start behaviour, exposed port, CPU/RAM and inference needs, persistent storage, secrets, restart behaviour and a realistic demo run. Replit Autoscale/Reserved VM publishing supports one external port; do not assume the development process layout can be published unchanged. Persist state in suitable database/object storage rather than relying on the published filesystem. [Ports](https://docs.replit.com/features/project-setup/ports); [publishing troubleshooting](https://docs.replit.com/build/troubleshooting).

Credits are a budget constraint, not proof of free or unlimited deployment. Check current account entitlements, shared Agent/cloud usage and spending controls before choosing a host. GPU-backed inference, if needed, belongs on RunPod under the competition rules; a CPU-compatible artifact may avoid an always-on GPU runtime. No deployment or paid resource creation is performed by adopting this document. [Replit Core billing](https://docs.replit.com/billing/plans/replit-core); [competition constraints](../PRD.md#competition-constraints).

## Decision maintenance

Update the decision table when the team settles an open choice, recording rationale, date and evidence in the relevant row. Product scope changes belong in PRD, model decisions in ML Design and data choices in Data Sources. Introduce a separate decision record only when the reasoning is substantial enough to need an independent history.

## ML foundation callable boundary

The later [foundation task](../ml/docs/MINDER_ML_FOUNDATION_CODEX_TASK.txt) authorizes `minder_ml.intelligence.recommend` under the existing `ml/src` package. The inspected `apps/backend-api` contains logical placeholders, with no application bootstrap or routes to extend. Therefore this task exposes a callable service and synthetic JSON example, without selecting a web framework. The [v1 machine-readable result contract](../contracts/recommendation-result.v1.schema.json) owns its exact structure; [foundation documentation](ml-foundation.md) owns its score semantics and verification. The broader HTTP proposal above remains unimplemented. No inference request starts training or silently substitutes the baseline for a requested learner.
