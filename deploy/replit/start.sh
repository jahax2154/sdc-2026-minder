#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$PWD/ml/src:$PWD/apps/backend-api"
export MINDER_HOSTING_TARGET=replit
exec .venv/bin/python -m deploy.replit_runtime
