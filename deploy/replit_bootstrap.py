"""Verify the module interpreter and built dependencies, then enter one launcher.

No installation, environment dump, provider call, database access or worker starts
during --check. Failure output uses fixed codes and source-controlled module names.
"""
import importlib
import importlib.metadata
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "jwt": "PyJWT", "clerk_backend_api": "clerk-backend-api",
    "psycopg": "psycopg", "replit.object_storage": "replit.object-storage",
    "cryptography": "cryptography", "httpx": "httpx", "pypdf": "pypdf",
    "numpy": "numpy", "scipy": "scipy", "sklearn": "scikit-learn",
    "xgboost": "xgboost-cpu" if sys.platform == "linux" else "xgboost",
}


class StartupFailure(Exception):
    pass


def verify(root=ROOT):
    if sys.version_info[:2] != (3, 12):
        raise StartupFailure("python_module_version_requires_3_12")
    site = root / ".pythonlibs/lib/python3.12/site-packages"
    if not site.is_dir():
        raise StartupFailure("built_dependency_directory_missing")
    try:
        import tomllib
        packages = tomllib.loads((root / "uv.lock").read_text())["package"]
        versions = {re.sub(r"[-_.]+", "-", p["name"].lower()): p.get("version") for p in packages}
    except Exception:
        raise StartupFailure("runtime_lock_unreadable") from None
    for module, distribution in REQUIRED.items():
        try:
            imported = importlib.import_module(module)
            location = Path(imported.__file__).resolve()
            version = importlib.metadata.version(distribution)
            expected = versions[re.sub(r"[-_.]+", "-", distribution.lower())]
            if not location.is_relative_to(site.resolve()) or version != expected:
                raise ValueError()
        except Exception:
            raise StartupFailure("required_import_or_pin_failed:" + module) from None
    for module in ("minder_app.api", "minder_app.hosted_worker", "minder_ml.intelligence.product_runtime"):
        try:
            importlib.import_module(module)
        except Exception:
            raise StartupFailure("application_import_failed:" + module) from None
    for name in ("apps/frontend-product/index.html", "apps/frontend-product/app.js",
                 "apps/frontend-product/auth.js"):
        if not (root / name).is_file():
            raise StartupFailure("frontend_asset_missing:" + name)
    try:
        from deploy.artifacts import inventory
        inventory(root=root, verify=True)
    except Exception:
        raise StartupFailure("runtime_data_verification_failed") from None
    return dict(event="minder_python_runtime_verified", python=sys.version.split()[0],
                executable=sys.executable, base_prefix=sys.base_prefix,
                dependency_directory=str(site), required_imports=len(REQUIRED),
                frontend_assets=True, runtime_data=True)


def main():
    if sys.argv[1:] not in ([], ["--check"]):
        print("minder_startup_fatal code=unsupported_start_argument", flush=True)
        raise SystemExit(2)
    print(json.dumps(dict(event="minder_python_runtime_probe", python=sys.version.split()[0],
                          executable=sys.executable, base_prefix=sys.base_prefix,
                          cwd=str(Path.cwd()), check_only=sys.argv[1:] == ["--check"])), flush=True)
    try:
        result = verify()
    except StartupFailure as error:
        print("minder_startup_fatal code=" + str(error), flush=True)
        raise SystemExit(1) from None
    print(json.dumps(result), flush=True)
    if sys.argv[1:] != ["--check"]:
        # Same process and same existing API/worker launcher; no second worker.
        runpy.run_module("deploy.replit_launch", run_name="__main__")


if __name__ == "__main__":
    main()
