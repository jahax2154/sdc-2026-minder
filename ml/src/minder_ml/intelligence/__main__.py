"""Run from repository root with PYTHONPATH=ml/src python3 -m minder_ml.intelligence."""

import argparse
import json
from pathlib import Path
import sys
import unittest

from . import recommend
from .schemas import FeatureSnapshot, RoleInput

ROOT = Path(__file__).resolve().parents[4]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("checks")
    sub.add_parser("preflight")
    validate = sub.add_parser("validate")
    validate.add_argument("--data", type=Path, required=True)
    for name in ("smoke", "compare"):
        command = sub.add_parser(name)
        command.add_argument("--run-id", required=True)
        command.add_argument("--runner-evidence", type=Path)
        if name == "smoke":
            command.add_argument("--fixture", type=Path, default=ROOT / "ml/tests/fixtures/synthetic_math.json")
        else:
            command.add_argument("--data", type=Path, required=True)
            command.add_argument("--split", type=Path)
    final = sub.add_parser("final")
    final.add_argument("--run-id", required=True)
    final.add_argument("--data", type=Path, required=True)
    score = sub.add_parser("score")
    score.add_argument("--input", type=Path, default=ROOT / "ml/tests/fixtures/example_request.json")
    score.add_argument("--scorer", choices=["baseline", "ridge", "xgboost"], default="baseline")
    score.add_argument("--model-version")
    args = parser.parse_args(argv)
    try:
        if args.mode == "checks":
            suite = unittest.defaultTestLoader.discover(str(ROOT / "ml/tests"), pattern="test_foundation.py")
            return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
        if args.mode == "preflight":
            from .artifacts import versions
            from .estimators import make_estimator, THREADS
            import platform
            output = {"platform": platform.platform(), "package_versions": versions(),
                      "thread_limit": THREADS, "fitting_performed": False, "estimators": {}, "errors": []}
            for kind in ("ridge", "xgboost"):
                try:
                    model = make_estimator(kind)
                    output["estimators"][kind] = {"construction": "passed", "pipeline_steps": list(model.named_steps)}
                except (ImportError, ValueError, OSError) as exc:
                    output["estimators"][kind] = {"construction": "failed", "error": str(exc)}
                    output["errors"].append(kind)
        elif args.mode == "validate":
            from .evaluation import read_annotations
            _, output = read_annotations(args.data)
        elif args.mode in ("smoke", "compare", "final"):
            from .training import smoke, compare, final_evaluate
            if args.mode == "smoke":
                output = smoke(args.run_id, args.fixture, args.runner_evidence)
            elif args.mode == "compare":
                output = compare(args.data, args.run_id, args.runner_evidence, args.split)
            else:
                output = final_evaluate(args.data, args.run_id)
        else:
            request = json.loads(args.input.read_text())
            roles = [RoleInput(r["role_id"], FeatureSnapshot.from_dict(r["features"]), r["evidence_ids"])
                     for r in request.pop("roles")]
            output = recommend(roles, **request, scorer_kind=args.scorer,
                               model_version=args.model_version).to_dict()
        print(json.dumps(output, indent=2, allow_nan=False))
        return 1 if output.get("errors") else 0
    except (OSError, ValueError, KeyError, ImportError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
