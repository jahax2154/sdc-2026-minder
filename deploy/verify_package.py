"""Test Docker's source layout offline without requiring Docker or live accounts."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from deploy.artifacts import ROOT, inventory

DIRECTORIES = ("ml/src", "ml/configs", "ml/data", "contracts", "apps/backend-api/minder_app",
               "apps/backend-api/data", "apps/frontend-product", "docs/execution/parallel",
               "docs/execution/product-v2", "deploy")
FILES = ("ml/minder_ml_starter/sources_manifest.json", "ml/docs/MINDER_POLICY_REVIEW_v1.md",
         "docs/execution/gates/G1A_v2_authorization.json")


def main():
    data = inventory(verify=True)
    with tempfile.TemporaryDirectory(prefix="minder-e-runtime-layout-") as directory:
        stage = Path(directory)
        for name in DIRECTORIES:
            shutil.copytree(ROOT / name, stage / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".env*", "*.sqlite*", "node_modules"))
        for name in FILES:
            (stage / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, stage / name)
        for item in data["sources"]:
            name = "ml/minder_ml_starter/" + item["relative_path"]
            (stage / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, stage / name)
            (stage / name).chmod(0o444)
        # No provider credentials/config or DB state enters this subprocess.
        environment = {key: value for key, value in os.environ.items() if key in ("PATH", "LANG", "LC_ALL", "SYSTEMROOT")}
        environment["PYTHONPATH"] = str(stage / "ml/src") + os.pathsep + str(stage / "apps/backend-api")
        program = """
import json
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.policy import load_policy
from minder_ml.intelligence.integration_cli import wsgi_request
from deploy.artifacts import inventory
inventory(verify=True)
app, _ = build('E')
code, result = wsgi_request(app,'GET','/api/health')
assert code == 200
assert len(app.services.roles) == 1016
load_policy()
code, session = wsgi_request(app,'POST','/api/session',{})
assert code == 200
code, resources = wsgi_request(app,'POST','/api/product/resources',{},session['token'])
assert code == 200 and resources['total'] == 2
print(json.dumps(dict(status='passed',source_layout='Docker-equivalent local filesystem',catalogue_roles=1016,
                     pinned_untracked_inputs=4,provider_calls=0,hosted=False,docker_build=False)))
"""
        subprocess.run([sys.executable, "-c", program], cwd=stage, env=environment, check=True)


if __name__ == "__main__":
    main()
