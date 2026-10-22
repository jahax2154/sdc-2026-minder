"""minder-data equivalent: python -m minder_ml.intelligence.data_cli COMMAND."""

import argparse
import json
from pathlib import Path
import sys

from .annotation_io import export_annotations, import_annotations
from .data_adapters import derive_profile
from .data_pipeline import PACK, SNAPSHOTS, ROOT, encoded, inspect_pack, prepare_snapshot, sha, acquire_market
from .data_schemas import validate_entity
from .market import build_market_views

PROFILE = ROOT / "ml/tests/fixtures/phase2_profile.synthetic.json"
ROLES = ROOT / "ml/data/review/phase2/roles.pending.json"


def read_records(path):
    path = Path(path)
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    result = json.loads(path.read_text())
    return result if isinstance(result, list) else [result]


def validate_records(rows):
    rejected = []
    for i, row in enumerate(rows):
        try:
            validate_entity(row)
        except ValueError as exc:
            rejected.append({"row": i + 1, "reason": str(exc)})
    return {"validated_rows": len(rows) - len(rejected), "rejected_rows": len(rejected), "rejections": rejected}


def validate_snapshot(path):
    path = Path(path)
    manifest = json.loads((path / "snapshot.json").read_text())
    for name, checksum in manifest["output_sha256"].items():
        if sha(path / name) != checksum:
            raise ValueError("frozen snapshot output checksum mismatch: " + name)
    return {"snapshot_id": manifest["snapshot_id"], **validate_records(read_records(path / "observations.jsonl"))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    acquire = sub.add_parser('market-acquire')
    acquire.add_argument('--max-details', type=int, default=40)
    acquire.add_argument('--output', type=Path, default=ROOT / 'ml/data/market/snapshot.v1.json')
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--pack", type=Path, default=PACK)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--pack", type=Path, default=PACK)
    prepare.add_argument("--output-root", type=Path, default=SNAPSHOTS)
    validate = sub.add_parser("validate")
    target = validate.add_mutually_exclusive_group(required=True)
    target.add_argument("--input", type=Path)
    target.add_argument("--snapshot", type=Path)
    market = sub.add_parser("market-build")
    market.add_argument("--snapshot", type=Path, required=True)
    export = sub.add_parser("annotation-export")
    export.add_argument("--profiles", type=Path, default=PROFILE)
    export.add_argument("--roles", type=Path, default=ROLES)
    export.add_argument("--output", type=Path, required=True)
    ingest = sub.add_parser("annotation-import")
    ingest.add_argument("--packet", type=Path, required=True)
    ingest.add_argument("--responses", type=Path, required=True)
    ingest.add_argument("--output", type=Path, required=True)
    report = sub.add_parser("report")
    report.add_argument("--snapshot", type=Path, required=True)
    report.add_argument("--profiles", type=Path, default=PROFILE)
    report.add_argument("--roles", type=Path, default=ROLES)
    report.add_argument("--review-results", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'market-acquire':
            output = acquire_market(output=args.output, max_details=args.max_details)
        elif args.command == "inspect":
            output = inspect_pack(args.pack)
        elif args.command == "prepare":
            output = prepare_snapshot(args.pack, args.output_root)
        elif args.command == "validate":
            output = validate_snapshot(args.snapshot) if args.snapshot else validate_records(read_records(args.input))
        elif args.command == "market-build":
            validation = validate_snapshot(args.snapshot)
            if validation["rejected_rows"]:
                raise ValueError("invalid canonical rows")
            views = build_market_views(read_records(args.snapshot / "observations.jsonl"))
            if encoded(views) != (args.snapshot / "views.json").read_text():
                raise ValueError("derived views differ from frozen snapshot")
            output = {"snapshot_id": validation["snapshot_id"], "validated_rows": validation["validated_rows"], "rejected_rows": 0,
                      "role_market_view_rows": len(views["role_market_view"]["rows"]),
                      "role_market_scope": views["role_market_view"]["status"],
                      "skill_market_view": views["skill_market_view"], "employer_market_view": views["employer_market_view"],
                      "market_score_policy": None}
        elif args.command == "annotation-export":
            output = export_annotations(read_records(args.profiles), read_records(args.roles), args.output)
        elif args.command == "annotation-import":
            output = import_annotations(args.packet, args.responses, args.output)
        else:
            validation = validate_snapshot(args.snapshot)
            profiles, roles = read_records(args.profiles), read_records(args.roles)
            for entity in profiles + roles:
                validate_entity(entity)
            review = json.loads(args.review_results.read_text()) if args.review_results else None
            output = {"snapshot": validation, "quality": json.loads((args.snapshot / "quality.json").read_text()),
                      "approved_roles": sum(r["review"]["status"] == "approved" for r in roles),
                      "profile_families": len({p["profile_family_id"] for p in profiles}),
                      "approved_profile_families": len({p["profile_family_id"] for p in profiles if p["review"]["status"] == "approved"}),
                      "review_readiness": review, "baseline_derivations": [derive_profile(p, roles, include_scores=True) for p in profiles],
                      "learner_training": "not_run", "weak_auto_labelling": "skipped; no provider or credentials introduced"}
        print(encoded(output), end="")
        return 1 if output.get("rejected_rows", 0) else 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(encoded({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr, end="")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
