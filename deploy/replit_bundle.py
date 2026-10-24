"""Carry frozen BUILD libraries in an explicit, non-hidden deployment output.

Not a venv export: no interpreter, activation scripts or pyvenv.cfg are copied.
Run only during build, never during application startup. Keep generated output
out of source checkpoints; validate in an isolated build checkout.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

from deploy.replit_bootstrap import ROOT, DEPENDENCY_DIRECTORY, verify

FORMAT = "minder-locked-python-libraries-v1"
MANIFEST = "minder-build.json"


def package(source, destination, lock):
    source, destination, lock = Path(source), Path(destination), Path(lock)
    if not source.is_dir() or source.is_symlink() or destination.is_symlink():
        raise ValueError("runtime_bundle_paths_invalid")
    if destination.exists():
        try:
            owned = json.loads((destination / MANIFEST).read_text())["format"] == FORMAT
        except Exception:
            owned = False
        if not owned:
            raise ValueError("runtime_bundle_destination_not_owned")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="minder-build-libs-", dir=destination.parent) as directory:
        staged = Path(directory) / "packages"
        shutil.copytree(source, staged, symlinks=False,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "_virtualenv.pth", "_virtualenv.py"))
        manifest = dict(format=FORMAT, lock_sha256=hashlib.sha256(lock.read_bytes()).hexdigest(),
                        python=sys.version.split()[0])
        (staged / MANIFEST).write_text(json.dumps(manifest) + "\n")
        # This build output must retain public wheel data such as certifi's PEM,
        # even when a publisher consults the source repository's ignore rules.
        (staged / ".gitignore").write_text("# Generated deployment libraries, not source checkpoints.\n!**\n")
        if destination.exists():
            shutil.rmtree(destination)  # Only the recognized generated output above.
        staged.rename(destination)
    return manifest


def main():
    if len(sys.argv) != 2:
        print("minder_build_fatal code=verified_build_site_argument_required", flush=True)
        raise SystemExit(2)
    source = Path(sys.argv[1])
    try:
        # Verify frozen build dependencies BEFORE copying only their library tree.
        verify(dependency_directory=source, require_bundle=False)
        manifest = package(source, ROOT / DEPENDENCY_DIRECTORY, ROOT / "uv.lock")
    except Exception:
        print("minder_build_fatal code=runtime_dependency_packaging_failed", flush=True)
        raise SystemExit(1) from None
    print(json.dumps(dict(event="minder_dependency_bundle_built", **manifest,
                          directory=DEPENDENCY_DIRECTORY)), flush=True)


if __name__ == "__main__":
    main()
