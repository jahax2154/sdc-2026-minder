#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import sys; assert sys.version_info[:2] == (3, 12), "Select Replit Python 3.12; storage SDK requires <3.13"'
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r deploy/requirements-hosted.lock.txt
export PYTHONPATH="$PWD/ml/src:$PWD/apps/backend-api"
.venv/bin/python -m deploy.artifacts fetch
.venv/bin/python -m pip check
.venv/bin/python -c 'import xgboost; assert xgboost.__version__ == "3.4.1"; print("CPU-compatible XGBoost import verified")'
