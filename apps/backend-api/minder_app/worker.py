"""Run in a dedicated local process. Deployment supervision belongs to A."""
import argparse
import json
import os
from pathlib import Path
import time
from .actions import ActionExecutor
from .agents import Worker
from .store import Store
from .config import configured_provider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--owner", help="Optional single-user scope for isolated local acceptance")
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    path = Path(os.environ.get("MINDER_DB_PATH", str(root / "ml/artifacts/session-c/runtime/dev.sqlite3"))).resolve()
    if not path.is_relative_to((root / "ml/artifacts/session-c").resolve()):
        raise ValueError("C worker database must stay under reserved Session C artifacts")
    store = Store(path)
    worker = Worker(store, ActionExecutor(store), provider=configured_provider())
    while True:
        result = worker.tick(owner=args.owner)
        print(json.dumps(result), flush=True)
        if args.once:
            return
        time.sleep(max(1, min(30, args.poll_seconds)))


if __name__ == "__main__":
    main()
