"""Operator commands over D's actual migration/backup services; no custom SQL."""
import argparse
import json
from pathlib import Path
from deploy.runtime import settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("backup", "migrate"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    database, _ = settings()
    if args.operation == "backup":
        if not database.is_file():
            raise ValueError("backup_source_database_missing")
        if args.output is None or not args.output.is_absolute():
            parser.error("backup requires a new absolute --output path")
        from minder_app.store import Store
        import os
        root = Path(os.environ["RAILWAY_VOLUME_MOUNT_PATH"]).resolve()
        if not args.output.resolve().is_relative_to(root / "backups"):
            raise ValueError("backup_destination_must_be_private_volume_backups")
        result = Store.on_volume(root, database).backup(args.output)
        print(json.dumps(result))
    else:
        from minder_ml.intelligence.product_runtime import build_hosted
        app = build_hosted(database=database)
        if getattr(app.store, "persistence_mode", None) != "mounted-sqlite":
            raise ValueError("verified_volume_store_required")
        print(json.dumps({"status": "migrated", "engine": app.store.engine,
                          "durability_status": app.store.durability_status, "worker_started": False}))


if __name__ == "__main__":
    main()
