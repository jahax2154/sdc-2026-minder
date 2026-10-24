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
        from minder_app.automation_state import save_automation_settings
        save_automation_settings(self.store, owner, {"enabled": enabled, "check_time": "00:00"}, None,
                                 at=datetime(2026, 10, 23, 0, 0, tzinfo=timezone.utc))
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
        from minder_app.automation_state import save_automation_settings
        save_automation_settings(self.store, owner, {"enabled": True}, old["version"], at=at)
        at += timedelta(days=1)
        with patch.object(worker, "analyse", side_effect=RuntimeError("private")):
            self.assertEqual(worker.tick(at, owner=owner)["status"], "retry")
            self.assertEqual(worker.tick(at + timedelta(seconds=1), owner=owner)["status"], "retry")
            self.assertEqual(worker.tick(at + timedelta(seconds=2), owner=owner)["status"], "failed")
        self.assertEqual(worker.tick(at + timedelta(seconds=3), owner=owner)["status"], "idle")
        self.assertEqual(state(self.store, owner)["notices"], [])
        self.assertEqual(self.store.get(owner, "agent_settings", owner)["last_result"]["status"], "failed")

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

    def test_canonical_cancel_invalidates_queued_and_inflight_work(self):
        from minder_app.automation_state import save_automation_settings
        owner, worker = self.setup_schedule()
        at = datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc)
        worker.daily(at, owner=owner)
        current = self.store.get(owner, "agent_settings", owner)
        cancelled = save_automation_settings(self.store, owner, {"state": "cancelled"}, current["version"], at=at)
        self.assertIsNone(cancelled["next_run"])
        self.assertEqual(worker.tick(at, owner=owner)["status"], "idle")
        self.assertTrue(all(e["status"] == "cancelled" for e in state(self.store, owner)["events"]))
        save_automation_settings(self.store, owner, {"state": "active"}, cancelled["version"], at=at)
        original = worker.analyse
        def cancel_during_analysis(event, instant):
            result = original(event, instant)
            current = self.store.get(owner, "agent_settings", owner)
            save_automation_settings(self.store, owner, {"state": "cancelled"}, current["version"], at=at)
            return result
        with patch.object(worker, "analyse", side_effect=cancel_during_analysis):
            self.assertEqual(worker.tick(at, owner=owner)["status"], "cancelled")
        self.assertEqual(state(self.store, owner)["notices"], [])
        self.assertTrue(all(e["status"] == "cancelled" for e in state(self.store, owner)["events"]))
        self.assertEqual(self.app.actions.history(owner), [])
        from minder_app.conversations import Conversations
        self.assertEqual(Conversations(self.store).mindbot(owner)["messages"], [])

    def test_canonical_timezone_catchup_and_last_result_use_actual_worker(self):
        from minder_app.automation_state import save_automation_settings
        owner, worker = self.setup_schedule()
        current = self.store.get(owner, "agent_settings", owner)
        # 01:00 UTC is09:00 MYT; profile timezone is deliberately different.
        profile = self.store.get(owner, "profile", owner)
        self.app.dispatch("PUT", "/api/profile", {"profile": {"timezone": "UTC"}, "expected_version": profile["version"]}, self.token)
        at = datetime(2026, 10, 24, 0, 0, tzinfo=timezone.utc)
        saved = save_automation_settings(self.store, owner,
            {"check_time": "09:00", "timezone": "Asia/Kuala_Lumpur", "state": "active"}, current["version"], at=at)
        self.assertEqual(saved["next_run"], "2026-10-24T01:00:00Z")
        self.assertEqual(worker.tick(at, owner=owner)["status"], "idle")
        # Miss two days: produce today's single due result, no historical replay.
        later = datetime(2026, 10, 26, 1, 0, tzinfo=timezone.utc)
        result = worker.tick(later, owner=owner)
        self.assertEqual(result["status"], "processed")
        self.assertEqual(worker.tick(later, owner=owner)["status"], "idle")
        saved = self.store.get(owner, "agent_settings", owner)
        self.assertEqual(saved["last_result"]["event_id"], result["event_id"])
        self.assertEqual(saved["last_result"]["status"], "processed")
        self.assertEqual(saved["next_run"], "2026-10-27T01:00:00Z")
        from minder_app.conversations import Conversations
        conversation = Conversations(self.store).mindbot(owner)
        self.assertEqual(saved["last_result"]["conversation_id"], conversation["conversation"]["conversation_id"])
        self.assertEqual(len(conversation["messages"]), 1)

    def test_actual_worker_limits_daily_analysis_to_selected_owned_plan(self):
        from support import fixture
        from minder_app.automation_state import save_automation_settings
        profile = self.save()
        owner = profile["profile_id"]
        empty = fixture("plan_progress")
        empty.update(profile_id=owner, tasks=[], task_ids=[])
        selected = self.app.dispatch("POST", "/api/plans", {"plan": empty, "idempotency_key": "selected"}, self.token)["plan"]
        other = fixture("plan_progress")
        other["profile_id"] = owner
        other["tasks"][0]["scheduled_at"] = "2026-10-23T00:00:00Z"
        other["tasks"][0]["estimated_hours"] = 1
        self.app.dispatch("POST", "/api/plans", {"plan": other, "idempotency_key": "excluded"}, self.token)
        save_automation_settings(self.store, owner, {"enabled": True, "check_time": "00:00",
            "scope": {"plan_ids": [selected["plan_id"]]}}, None,
            at=datetime(2026, 10, 23, 0, 0, tzinfo=timezone.utc))
        worker = Worker(self.store, self.app.actions, services=None)
        self.assertEqual(worker.tick(datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc), owner=owner)["status"], "processed")
        notice = state(self.store, owner)["notices"][0]
        self.assertIn("0/0", notice["summary"])
        self.assertNotIn("proposal", notice)
        self.assertEqual(self.app.actions.proposals(owner), [])
