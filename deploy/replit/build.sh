#!/usr/bin/env bash
set -euo pipefail
taskRoot="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
cd "$taskRoot"
source "$taskRoot/deploy/replit/python.sh"
taskPython="$(minder_module_python)"
"$taskPython" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Replit Python module must be 3.12"'
taskBuildRoot="$(mktemp -d "${TMPDIR:-/tmp}/minder-python-build.XXXXXX")"
trap 'rm -rf -- "$taskBuildRoot"' EXIT
taskBuildEnv="$taskBuildRoot/environment"
UV_PROJECT_ENVIRONMENT="$taskBuildEnv" uv sync --frozen --no-dev --python "$taskPython"
taskBuildSite="$taskBuildEnv/lib/python3.12/site-packages"
export PYTHONPATH="$taskBuildSite:$taskRoot/ml/src:$taskRoot/apps/backend-api"
"$taskPython" -m deploy.artifacts fetch
uv pip check --python "$taskBuildEnv/bin/python"
"$taskPython" -m deploy.replit_bundle "$taskBuildSite"
export PYTHONPATH="$taskRoot/deploy/replit/runtime_packages:$taskRoot/ml/src:$taskRoot/apps/backend-api"
"$taskPython" -m deploy.replit_bootstrap --check
