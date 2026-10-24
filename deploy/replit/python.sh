#!/usr/bin/env bash
# Select only the Python module supplied by Replit/Nix, never a workspace venv.
minder_module_python() {
  local candidate
  while IFS= read -r candidate; do
    case "$candidate" in
      /nix/store/*/bin/python3)
        printf '%s\n' "$candidate"
        return 0
        ;;
    esac
  done < <(type -a -p python3)
  printf '%s\n' 'minder_startup_fatal code=replit_module_python_missing' >&2
  return 127
}
