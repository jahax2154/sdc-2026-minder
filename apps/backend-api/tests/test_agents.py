from datetime import datetime, timezone
from support import AppCase, fixture
from minder_app.agents import Worker, configure, emit, state, market_event
from minder_app.plans import save_plan


class AgentTests(AppCase):
    def test_scoped_worker_leaves_other_user_events_untouched(self):
        owner = self.save()["profile_id"]
        other = self.store.session()["profile_id"]
        with self.store.transaction() as db:
            emit(db, other, "other-event", "daily_check", {})
            emit(db, owner, "own-event", "task_completion", {})
        worker = Worker(self.store, self.app.actions)
        self.assertEqual(worker.tick(owner=owner)["status"], "processed")
        self.assertEqual(state(self.store, other)["events"][0]["status"], "pending")

    def test_market_relevance_dedupe_and_explicit_profile_triggers(self):
        profile = self.save()
        source = profile["evidence"][0]["provenance"].copy()
        source.update(evidence_type="source-derived", uri="https://example.org/evidence")
        self.assertEqual(market_event(self.store, profile["profile_id"], "m1", ["unrelated"], [source])["status"],
                         "irrelevant_no_notice")
        for _ in range(2):
            market_event(self.store, profile["profile_id"], "m1", ["synthetic-skill"], [source])
        self.assertEqual(len(state(self.store, profile["profile_id"])["events"]), 1)
        profile["preferences"][0]["state"] = "interested"
        self.app.dispatch("PUT", "/api/profile", dict(profile=profile, expected_version=profile["version"]), self.token)
        self.assertIn("preferences_changed", [e["kind"] for e in state(self.store, profile["profile_id"])["events"]])

    def test_daily_timezone_dedupe_proposal_approval_and_completion(self):
        plan = self.make_plan()["plan"]
        plan["tasks"][0]["estimated_hours"] = 1
        plan["constraints"] = [dict(constraint_id="hours", scope="weekly_hours", hard=True,
            value=5, unit="hours_per_week", evidence_id="self-report")]
        plan = save_plan(self.store, self.profile["profile_id"], plan, plan["state_version"])["plan"]
        configure(self.store, self.profile["profile_id"], dict(enabled=True, check_time="08:00"), None)
        worker = Worker(self.store, self.app.actions)
        before_check = datetime(2026, 10, 26, 23, 59, tzinfo=timezone.utc)
        worker.daily(before_check)
        self.assertFalse(state(self.store, self.profile["profile_id"])["events"])
        at = datetime(2026, 10, 27, 0, 1, tzinfo=timezone.utc)  # 08:01 MYT
        self.assertEqual(worker.tick(at)["status"], "processed")
        self.assertEqual(worker.tick(at)["status"], "idle")
        result = state(self.store, self.profile["profile_id"])
        self.assertEqual(len(result["notices"]), 1)
        self.assertEqual(self.store.get(self.profile["profile_id"], "plan", plan["plan_id"]), plan)
        notice = result["notices"][0]
        proposal = notice["proposal"]
        approved = self.app.actions.decide(self.profile["profile_id"], proposal["preview"]["proposal_id"],
            "approve", proposal["preview_hash"], plan["state_version"])
        self.assertEqual(approved["action"]["execution_status"], "applied")
        self.assertFalse(result["deployment_scheduler_verified"])

    def test_bound_retry_and_task_completion_trigger(self):
        plan, req = self.setup_request()
        self.app.actions.direct(self.profile["profile_id"], req, "complete")
        self.assertEqual(state(self.store, self.profile["profile_id"])["events"][0]["kind"], "task_completion")
        worker = Worker(self.store, self.app.actions)
        def fail(*args):
            raise RuntimeError("private must not leak")
        worker.analyse = fail
        for expected in ("retry", "retry", "failed", "idle"):
            self.assertEqual(worker.tick()["status"], expected)
        self.assertNotIn("private", str(state(self.store, self.profile["profile_id"])))
