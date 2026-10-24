#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$PWD/ml/src:$PWD/apps/backend-api"
export MINDER_HOSTING_TARGET=replit
exec .pythonlibs/bin/python -m deploy.replit_launch
