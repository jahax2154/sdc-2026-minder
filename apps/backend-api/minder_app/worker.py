"""Run in a dedicated local process. Deployment supervision belongs to A."""
import argparse
import json
import os
from pathlib import Path
import time
from .actions import ActionExecutor
from .agents import Worker
from .store import Store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    store = Store(os.environ.get("MINDER_DB_PATH", str(root / "ml/artifacts/session-c/runtime/dev.sqlite3")))
    worker = Worker(store, ActionExecutor(store))
    while True:
        result = worker.tick()
        print(json.dumps(result), flush=True)
        if args.once:
            return
        time.sleep(30)


if __name__ == "__main__":
    main()
