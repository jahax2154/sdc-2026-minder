# ml

**PROPOSED:** Offline data preparation, configurations, experiments and evaluation. Existing source/test placeholders are preserved. Dataset, target, model framework and inference integration are **PENDING**. RunPod is required if training or fine-tuning is performed; neither is authorized here.

## Authorized ML foundation

The subsequent [foundation task](docs/MINDER_ML_FOUNDATION_CODEX_TASK.txt) authorizes the fixed baseline, Ridge and CPU XGBoost paths under `src/minder_ml/intelligence`. Earlier Task 001 restrictions above describe the scaffolding phase. See [implementation, commands and limitations](../docs/ml-foundation.md), [result contract](../contracts/recommendation-result.v1.schema.json), and [recorded checks](evaluation/foundation_checks.json). Baseline is the default; learner training/evaluation is not claimed merely by delivering code.
