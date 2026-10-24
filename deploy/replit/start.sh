#!/usr/bin/env bash
set -euo pipefail
taskRoot="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
printf 'minder_startup_paths cwd=%q root=%q\n' "$PWD" "$taskRoot"
cd "$taskRoot"
for taskPath in .pythonlibs .pythonlibs/pyvenv.cfg .pythonlibs/bin/python .pythonlibs/lib/python3.12/site-packages; do
  printf 'minder_startup_path path=%q exists=%s executable=%s symlink=%s\n' "$taskPath" "$([[ -e "$taskPath" ]] && printf yes || printf no)" "$([[ -x "$taskPath" ]] && printf yes || printf no)" "$([[ -L "$taskPath" ]] && printf yes || printf no)"
  if [[ -L "$taskPath" ]]; then printf 'minder_startup_link path=%q target=%q\n' "$taskPath" "$(readlink "$taskPath")"; fi
done
source "$taskRoot/deploy/replit/python.sh"
taskPython="$(minder_module_python)"
printf 'minder_startup_python selected=%q\n' "$taskPython"
export PYTHONPATH="$taskRoot/.pythonlibs/lib/python3.12/site-packages:$taskRoot/ml/src:$taskRoot/apps/backend-api"
export MINDER_HOSTING_TARGET=replit
exec "$taskPython" -m deploy.replit_bootstrap "$@"
