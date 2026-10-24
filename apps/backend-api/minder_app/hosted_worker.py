"""Supervise the existing persisted worker; no new scheduler or state writes."""
import json
import threading
from .agents import Worker


def run(app, *, stop_event=None, poll_seconds=30, once=False, worker=None, report=None):
    stop_event = stop_event if stop_event is not None else threading.Event()
    if not 1 <= poll_seconds <= 60:
        raise ValueError("invalid_hosted_worker_poll_interval")
    selected = worker if worker is not None else getattr(app, "scheduled_worker", None)
    if selected is None:
        selected = Worker(app.store, app.actions, provider=app.provider, services=app.services)
    report = report if report is not None else lambda item: print(json.dumps(item), flush=True)
    while not stop_event.is_set():
        from .conversations import reconcile_notices
        # Recover persisted outputs only; do not replay a processed job/action.
        reconcile_notices(app.store, limit=50)
        result = selected.tick()
        # Worker notices can contain private user/source data; log status only.
        report({key: result[key] for key in ("status", "code") if key in result})
        if once:
            return result
        stop_event.wait(poll_seconds)
    return {"status": "stopped"}
