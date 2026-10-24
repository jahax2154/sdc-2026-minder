#!/usr/bin/env bash
set -euo pipefail
taskRoot="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
cd "$taskRoot"
source "$taskRoot/deploy/replit/python.sh"
taskPython="$(minder_module_python)"
"$taskPython" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Replit Python module must be 3.12"'
UV_PROJECT_ENVIRONMENT="$taskRoot/.pythonlibs" uv sync --frozen --no-dev --python "$taskPython"
export PYTHONPATH="$taskRoot/.pythonlibs/lib/python3.12/site-packages:$taskRoot/ml/src:$taskRoot/apps/backend-api"
"$taskPython" -m deploy.artifacts fetch
uv pip check --python .pythonlibs/bin/python
"$taskPython" -m deploy.replit_bootstrap --check
