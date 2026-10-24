from datetime import datetime, timezone, timedelta
import threading
from unittest.mock import Mock, patch
from support import AppCase
from minder_app.agents import Worker, configure, state
from minder_app.hosted_worker import run


class HostedWorkerTests(AppCase):
    def setup_schedule(self, enabled=True):
        self.save()
        owner = self.session["profile_id"]
        configure(self.store, owner, {"enabled": enabled, "check_time": "00:00"}, None)
        return owner, Worker(self.store, self.app.actions, services=None)

    def test_real_due_daily_without_browser_is_persisted_and_deduplicated(self):
        owner, worker = self.setup_schedule()
        at = datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc)
        result = worker.tick(at, owner=owner)
        self.assertEqual(result["status"], "processed")
        self.assertEqual(worker.tick(at, owner=owner)["status"], "idle")
        notices = state(self.store, owner)["notices"]
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0]["trigger"], "daily_check")
        from minder_app.store import Store
        self.assertEqual(state(Store(self.store.path), owner)["notices"], notices)
        from minder_app.conversations import Conversations
        conversation = Conversations(self.store).mindbot(owner)
        self.assertEqual(len(conversation["messages"]), 1)
        reopened = Conversations(Store(self.store.path)).mindbot(owner)
        self.assertEqual(reopened, conversation)

    def test_pause_after_due_enqueue_suppresses_pending_notice(self):
        owner, worker = self.setup_schedule()
        at = datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc)
        worker.daily(at, owner=owner)
        old = self.store.get(owner, "agent_settings", owner)
        configure(self.store, owner, {"enabled": False, "check_time": "00:00"}, old["version"])
        # A suppresses queued work during configure; a later tick stays idle.
        self.assertEqual(worker.tick(at, owner=owner)["status"], "idle")
        self.assertEqual(state(self.store, owner)["notices"], [])

    def test_disabled_schedule_does_not_enqueue_and_failed_work_retries_bounded(self):
        owner, worker = self.setup_schedule(enabled=False)
        at = datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc)
        self.assertEqual(worker.tick(at, owner=owner)["status"], "idle")
        old = self.store.get(owner, "agent_settings", owner)
        configure(self.store, owner, {"enabled": True, "check_time": "00:00"}, old["version"])
        with patch.object(worker, "analyse", side_effect=RuntimeError("private")):
            self.assertEqual(worker.tick(at, owner=owner)["status"], "retry")
            self.assertEqual(worker.tick(at + timedelta(seconds=1), owner=owner)["status"], "retry")
            self.assertEqual(worker.tick(at + timedelta(seconds=2), owner=owner)["status"], "failed")
        self.assertEqual(worker.tick(at + timedelta(seconds=3), owner=owner)["status"], "idle")
        self.assertEqual(state(self.store, owner)["notices"], [])

    def test_wrapper_stop_once_and_logs_no_private_fields(self):
        worker = Mock()
        worker.tick.return_value = {"status": "processed", "notice": "private text", "owner": "private-owner"}
        report = Mock()
        run(self.app, once=True, worker=worker, report=report)
        report.assert_called_once_with({"status": "processed"})
        stop = threading.Event()
        stop.set()
        self.assertEqual(run(self.app, stop_event=stop, worker=worker)["status"], "stopped")
        self.assertEqual(worker.tick.call_count, 1)
