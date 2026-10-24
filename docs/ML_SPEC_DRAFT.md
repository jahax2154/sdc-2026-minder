# ML specification draft

Status: **PENDING** approval. This file reserves decisions; no datasets, algorithms or models have been selected or implemented.

| Section | Pending specification |
| --- | --- |
| Dataset | Sources, licensing/consent, provenance, access, privacy, representativeness and split strategy |
| Prediction target | Career decision-support target, intended use and ground truth definition |
| Features | Available inputs, profile/market evidence, transformations and leakage controls |
| Algorithms | Candidate approaches justified against the approved target and data |
| Baselines | Simple comparison approach and reproducible reference results |
| Evaluation metrics | Task metrics, scenario checks, subgroup performance and acceptance criteria |
| Training infrastructure | Reproducibility, compute budget and artifact handling; RunPod required if training or fine-tuning occurs |
| Model limitations | Bias, uncertainty, data freshness, generalization and constraints on career projections |

**PROPOSED** organization: `data` for data-handling guidance, `configs` for future configurations, `experiments` for future experiment records, and `evaluation` for future evaluation specifications. Existing `src/minder_ml` and `tests` are retained placeholders. Inference serving and the role of LLMs versus predictive models remain **PENDING**. Do not add raw/private data or weights to Git. No training or fine-tuning is authorized by Task 001.
