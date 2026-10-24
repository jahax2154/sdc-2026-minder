# Minder — SDC Hackathon 2026

Minder is an AI-assisted career exploration and personalised reskilling prototype for students, fresh graduates and career switchers. It combines supported occupational requirements, scoped Malaysian market evidence and user-provided background with learning plans and conversational guidance.

## Team information

| Field | Details |
| --- | --- |
| Team name | AINewBee |
| Domain | Domain 1 — The Aiversecity Future-Ready Workforce Domain |
| SDG track | SDG 4 — Quality Education |
| Team leader | Lee Yi Cheng |
| Universities | Asia Pacific University of Technology & Innovation (APU); Universiti Teknologi Malaysia (UTM) |
| Members | 3 |

## Preview and submission links

| Resource | Link |
| --- | --- |
| GitHub repository | https://github.com/jahax2154/sdc-2026-minder |
| Public **static interface preview** | https://aesthetic-baklava-2da854.netlify.app |
| Slide deck | https://canva.link/67te6g9azdjgt61 |
| Demo video | https://youtu.be/l9xjHBjcycM |
| Submission document | [Uploaded submission template](submission/AI%20Newbee_Submission_Template.docx) |
| Technical and tools declaration | [Uploaded declaration](submission/AI%20Newbee_Technical_Tools_Declaration_Review-2.docx) |
| Replit proof of use | [Submitted PDF](submission/AINewBee_Replit_POU.pdf) |
| RunPod proof of use | [Submitted PDF](submission/AINewBee_Runpod_POU.pdf) |
| RunPod experiment console | https://console.runpod.io/serverless/user/endpoint/0387furb08gke2 |

The Netlify URL serves the separate read-only export in `apps/frontend-product/netlify-drop/`. It shows explicitly labelled synthetic examples of the interface. Navigation and example views work; live AI, real login, CV uploads, saved profile/plan/task changes and scheduled actions are unavailable there. It neither hosts nor connects to the Python backend. The RunPod console link requires its owner's account; it is not a public career-chat endpoint.

**The full application source is included in this repository. A public full-stack deployment has not passed acceptance.** Replit native builds and dependency checks passed, but the latest verified published startup failed its required-data inventory guard. Managed-user login, production persistence, restart and scheduled delivery remain unverified. Provider-side deployment experiments remain separate from the static preview and are not submission proof of a working backend.

## What the full application implements

- Short onboarding collects background, interests or uncertainty, and self-reported experience, including none. It can return up to five labelled provisional starting directions without requiring a CV or a complete competency rubric. Unknown competence is not a numerical zero.
- The assessed recommendation policy retains separate demonstrated skills, transferable background, role/industry preferences and work-style evidence. Backend calculations determine rankings; comparable current market evidence has explicitly scoped influence. The model does not invent fit scores.
- A selected direction can receive a real Qwen-generated structured plan. Explicit acceptance saves one canonical plan used by the distinct Skills, Next Steps, Roadmap and Progress views. Task completion records activity progress, not proven skill mastery.
- Minder provides persisted conversation history and source-backed market/career answers. General search discovery, fetching predefined public sources and reading stored evidence remain distinct operations. Advice is distinguished from measured findings; supporting sources retain dates and geographic scope.
- Minder change requests can produce one linked proposal in the user's single Mindbot conversation. Rejection preserves state; approval validates ownership/current versions and executes once. Questions alone do not modify records. Direct-action authority elsewhere remains scoped.
- Profile/CV services support bounded PDF and UTF-8 TXT uploads, extraction review and private storage where configured. DOCX upload is not supported by this implementation. A CV is optional for initial directions.
- The existing worker supports persisted in-app automation. Local service tests and hosted delivery acceptance are separate.

Current Malaysian evidence has limited comparable role coverage. Occupational requirements are not proof of a user's proficiency or Malaysian hiring demand. Real next-quarter forecasts, AI-replacement probabilities and independently validated career-outcome accuracy are unavailable. Hypothetical/synthetic experiments are labelled accordingly.

## Actual technology and source structure

| Layer | Implementation in this release |
| --- | --- |
| Product frontend | Dependency-free JavaScript ES modules, HTML and CSS in `apps/frontend-product/` |
| Backend | Python WSGI API and bounded concurrent server in `apps/backend-api/` and `ml/src/minder_ml/intelligence/` |
| Contracts | JSON schemas and typed request/response validation in `contracts/` and backend schema modules |
| Local state | Isolated SQLite databases; owner-scoped profiles, conversations, plans, tasks and document metadata |
| Hosted adapters | Native PostgreSQL, Clerk verified identity and private Replit App Storage; hosted acceptance pending |
| Model | Server-side Groq `qwen/qwen3.8-27b`, bounded shared usage and explicit failures |
| Recommendations | Versioned assessed and starter policies, occupational mappings and typed market evidence |
| Experiments | Baselines, Ridge and XGBoost; separate bounded RunPod CUDA experiment on synthetic targets |

```text
apps/backend-api/                  Full Python API, services, state and tests
apps/frontend-product/             Working full-app frontend and browser checks
  netlify-drop/                    Separate read-only static preview export
  tools/export_static_preview.py   Reproducible preview exporter
apps/frontend-web/                 Earlier acceptance frontend, preserved
contracts/                         Shared schemas and contracts
ml/src/minder_ml/                  Scoring, catalogue, evidence and ML code
ml/configs/                        Versioned policies and configuration
ml/tests/                          ML and policy tests
ml/minder_ml_starter/               Source manifest; licensed raw inputs supplied separately
deploy/                            Hosting adapters, artifact provisioner and checks
docs/execution/                    Phase history, handoffs and acceptance evidence
submission/                        Teammate-uploaded submission and proof-of-use files
pyproject.toml / uv.lock            Locked Python runtime dependencies
```

The historical React/Express architecture proposals are retained in project history; they do not describe this released Python/ES-module implementation. The Netlify export does not replace any API, ML or full-app frontend source.

## Run the full application locally

Prerequisites: Git, Python **3.12**, and `uv`. Run these from a fresh clone of this repository. The UI needs no Node build. Use a private server-side Groq key for real model generation; keep the verified model ID. Without that credential, non-model functions remain usable and generation reports unavailable rather than fabricated success.

```sh
git clone https://github.com/jahax2154/sdc-2026-minder.git
cd sdc-2026-minder
uv sync --frozen --no-dev --python 3.12
export PYTHONPATH=ml/src:apps/backend-api

# Fetch only four existing allowlisted, hash-pinned O*NET 31.0 public inputs.
# Existing mismatched files are never overwritten; source bytes stay read-only.
uv run --frozen --no-dev python -m deploy.artifacts fetch

# Configure GROQ_API_KEY privately in the server environment, or in the
# owner-only .env.groq.local file (chmod 600); never put it in frontend code.
export GROQ_MODEL=qwen/qwen3.8-27b
export MINDER_ENV=development
export MINDER_DOCUMENT_STORAGE=local-development
uv run --frozen --no-dev python -m minder_ml.intelligence.product_runtime --lane A --worker
```

Open **http://127.0.0.1:9111**; the private API is on **http://127.0.0.1:8111**, also proxied by the UI's same-origin `/api`. Lane A stores its SQLite database/uploads under ignored `ml/artifacts/session-a/product/`. Local sessions are development identities, not managed hosted accounts. Do not use another lane's database or expose this local mode publicly. Localhost is not a teammate's remote backend.

For the existing Session A workstation, reuse its private environment with `source .env.local` and `PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane A --worker`; do not recreate its DB or copy credentials.

The four public inputs can be reproduced through [the pinned provisioner](deploy/artifacts.py) and [attribution](deploy/ATTRIBUTION.md). Additional historical/training inputs, weights, real profiles/CVs, credentials and private databases are deliberately not distributed. Full historical input verification requires the authorised 13-input pack described in [the source handoff](docs/execution/parallel/A/checks/provision_dev_inputs.py); those extra inputs are not universal startup prerequisites.

### Checks

```sh
export PYTHONPATH=ml/src:apps/backend-api
uv run --frozen --no-dev python -m unittest discover -s apps/backend-api/tests
uv run --frozen --no-dev python -m unittest discover -s deploy -p 'test_*.py'
git diff --check
```

Browser checks are in `apps/frontend-product/tests/` and `docs/execution/product-v2/checks/`. They require a separate Playwright/browser installation; some explicitly use fixtures and some make real provider calls. Read the named check before running it. Do not count fixture checks as real-provider or hosted acceptance.

## Replit, RunPod and evidence

Replit was used for integration and native Linux build/runtime diagnosis. The retained [Replit guide](deploy/replit/README.md) and [latest release record](docs/execution/product-v2/RELEASE_MAIN_INTEGRATION.md) describe the actual boundaries. A passing build or preview health check is not a working public backend. This release does not request another deployment or billing change.

B completed one bounded RunPod CUDA experiment on an RTX A4500: five XGBoost fits used CUDA, while Ridge and baseline runs used CPU. The test targets were synthetic; XGBoost performed worse than the baselines and was not promoted into application ranking or real forecasts. Returned model weights remain outside Git; configuration, numerical results and hash manifests are included. Cleanup verified zero workers and no queued/running jobs. See [GPU handoff](docs/execution/parallel/B/GPU_HANDOFF.v1.md) and [observed credit reconciliation](docs/execution/parallel/B/MB2-R01.json). No rerun is required to start Minder.

Relevant acceptance records:

- [Fresh normal-onboarding, real plan, canonical state and approval journey](docs/execution/product-v2/A_N9_3_COMBINED_JOURNEY.md)
- [Real browser answer synthesis, dated sources and Qwen output](docs/execution/product-v2/A_N11_ACCEPTANCE_AND_E_HANDOFF.md)
- [Actual native PostgreSQL/private-storage handoff](docs/execution/product-v2/D/REPLIT_PERSISTENCE_HANDOFF.md)
- [Scoring/evidence pipeline and worked example](docs/execution/product-v2/PITCH_PIPELINE.md)
- [Canonical decisions](docs/MINDER_AI_ML_DECISION_CONTEXT.md) and [current ownership](docs/execution/product-v2/OWNERSHIP.json)

Earlier reports remain chronological evidence. Their historical passing counts, pending gates or obsolete setup instructions should not override the latest release record.

## Team and lessons

| Name | Contribution | GitHub |
| --- | --- | --- |
| Lee Yi Cheng | Full-stack development, interface design, API integration and deployment collaboration | [@yicheng-0612](https://github.com/yicheng-0612) |
| Phuah Jun Hong | Machine learning, model experiments, evidence and application integration, RunPod work | [@jahax2154](https://github.com/jahax2154) |
| Lau Wen Le | Documentation, project coordination, presentation and submission preparation | [@WenLe0317](https://github.com/WenLe0317) |

The work reinforced the need for shared API contracts, explicit ownership, clear UI limitations and evidence-backed recommendations. Published programme descriptions, attention and synthetic targets cannot substitute for current hiring measurements. Future work includes broader comparable Malaysian evidence, independent evaluation, multilingual support and completing hosted authentication/durability/delivery acceptance.

## Submission status

The uploaded DOCX submission/declaration files and both proof-of-use PDFs are linked above and preserved as submitted. Slide and video links are retained from the team's latest README. A final preliminary PDF or declaration PDF is not present under the older README's proposed filenames; do not treat those missing exports as delivered. The confirmed public URL is the static preview only. Forecasting accuracy and a public full-stack backend remain limitations.

## License

[Apache License 2.0](LICENSE). Source data and imported assets retain their separately documented licences and attribution.
