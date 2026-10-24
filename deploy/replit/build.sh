#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import sys; assert sys.version_info[:2] == (3, 12), "Select Replit Python 3.12; storage SDK requires <3.13"'
UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --frozen --no-dev
export PYTHONPATH="$PWD/ml/src:$PWD/apps/backend-api"
.pythonlibs/bin/python -m deploy.artifacts fetch
uv pip check --python .pythonlibs/bin/python
.pythonlibs/bin/python -c 'import xgboost; assert xgboost.__version__ == "3.4.1"; print("CPU-compatible XGBoost import verified")'
