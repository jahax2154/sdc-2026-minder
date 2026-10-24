# Minder — SDC Hackathon 2026

Career decision-support prototype for SDC Hackathon 2026. Minder is the provisional product name.

The integrated prototype now includes the Python API, approved product frontend,
persisted profiles/conversations/CVs, backend recommendations, real Qwen guidance
and validated actions. **Local core acceptance is verified; the full frontend gate,
hosted login/durability and compulsory GPU execution remain incomplete.**
There is no accepted public demo URL yet.

Latest [Home/chat integration and acceptance](docs/execution/product-v2/A_UX3_CURRENT_HANDOFF.md)
includes saved bot customization and owned history search. Core local journeys and
real Qwen roadmap/follow-up/actions pass; two small F-owned pagination/undated-label
checks remain open. B's native-build source is now published; actual GPU fitting is
still pending. Keep these local results separate from hosted/login acceptance.

## Run the existing isolated A prototype

```sh
cd /Users/phuahjunhong/sdc-2026-minder-worktrees/session-a
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane A --worker
```

Use the existing private Python3.12 environment/configuration. UI:
http://127.0.0.1:9111; API: http://127.0.0.1:8111 or same-origin `/api`.
Local anonymous sessions are development identities, not hosted login. Localhost
is not a remote teammate backend. Never copy provider keys into the browser.

For another machine or the selected Railway candidate, use the reproducible
[deployment instructions](deploy/README.md), dependency lock and pinned public
artifact provisioner. Its managed authentication and mounted private volume are
required; missing configuration fails closed. Do not reuse another lane's database.

## Release evidence and demo

- [Release candidate, five-minute walkthrough and outstanding gates](docs/execution/product-v2/MORNING_RELEASE_CANDIDATE.md)
- [Measured acceptance and evidence distinctions](docs/execution/product-v2/MA2_ACCEPTANCE.json)
- [Full checkpoint ancestry index](docs/execution/product-v2/MORNING_CHECKPOINTS.json)
- [Active scoring/evidence pipeline and worked example](docs/execution/product-v2/PITCH_PIPELINE.md)
- [Current ownership](docs/execution/product-v2/OWNERSHIP.json) and [approved designs](docs/minder-approved-product-designs/MANIFEST.json)

Runtime code is in `apps/backend-api`, `apps/frontend-product` and `ml/src`.
The active scorer is provisional; the LLM explains evidence and proposes learning
steps, while backend calculations determine ranking. Current Malaysian evidence
has limited comparable role coverage. Real future forecasts and independently
validated career-outcome accuracy are unavailable. Preserved Ridge/XGBoost
experiments do not establish those claims.

Historical scaffold/architecture proposals retain their original approval status.
Read [canonical decision context](docs/MINDER_AI_ML_DECISION_CONTEXT.md),
[Revision3 runbook](docs/Minder_Morning_Completion_Runbook_2026-10-24.md),
[AGENTS.md](AGENTS.md) and the decision log before further engineering work.
Release PR preparation does not authorize merging main or publishing a tag.
