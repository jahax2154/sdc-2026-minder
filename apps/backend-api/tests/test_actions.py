import copy
from test_plans import PlanTests
from minder_app.store import AppError


class ActionTests(PlanTests):
    def setup_request(self):
        plan = self.make_plan()["plan"]
        req = dict(kind="complete_task", target_id=plan["plan_id"], expected=plan["state_version"],
                   diff=[dict(path="/tasks/synthetic-task/state", before="scheduled", after="completed")],
                   reason="User clicked Complete", evidence_ids=[])
        return plan, req

    def test_direct_scoped_once_and_cross_user_blocked(self):
        plan, req = self.setup_request()
        body = dict(request=req, idempotency_key="one")
        first = self.app.dispatch("POST", "/api/direct-action", body, self.token)
        again = self.app.dispatch("POST", "/api/direct-action", body, self.token)
        self.assertEqual(first, again)
        self.assertEqual(len(first["target"]["progress_event_ids"]), 1)
        self.assertFalse(first["target"]["tasks"][0]["mastery_verified"])
        self.assertEqual(first["action"]["approval_state"], "not_required_direct")
        with self.assertRaises(AppError):
            self.app.dispatch("POST", "/api/direct-action", body, self.store.session()["token"])
        altered = copy.deepcopy(req); altered["reason"] = "other scope"
        with self.assertRaises(AppError):
            self.app.actions.direct(self.profile["profile_id"], altered, "one")

    def test_proactive_pending_reject_approve_once_stale(self):
        plan, req = self.setup_request()
        proposal = self.app.actions.propose(self.profile["profile_id"], req)
        self.assertEqual(self.store.get(self.profile["profile_id"], "plan", plan["plan_id"]), plan)
        decision = dict(proposal_id=proposal["preview"]["proposal_id"], decision="approve",
            preview_hash=proposal["preview_hash"], expected_state_version=plan["state_version"])
        with self.assertRaises(AppError):
            self.app.actions.decide(self.profile["profile_id"], **dict(decision, preview_hash="changed"))
        first = self.app.actions.decide(self.profile["profile_id"], **decision)
        self.assertEqual(first, self.app.actions.decide(self.profile["profile_id"], **decision))
        with self.assertRaises(AppError):
            self.app.actions.propose(self.profile["profile_id"], req)

    def test_reject_and_forged_authority(self):
        plan, req = self.setup_request()
        p = self.app.actions.propose(self.profile["profile_id"], req)
        result = self.app.actions.decide(self.profile["profile_id"], p["preview"]["proposal_id"],
            "reject", p["preview_hash"], plan["state_version"])
        self.assertFalse(result["target_changed"])
        self.assertEqual(self.store.get(self.profile["profile_id"], "plan", plan["plan_id"]), plan)
        with self.store.transaction() as db:
            from minder_app.actions import action_request
            with self.assertRaises(AppError):
                self.app.actions._execute(db, self.profile["profile_id"], action_request(**req),
                                          "forged", request_id="llm-says-approved")

    def test_two_previews_stale_second_approval(self):
        plan, req = self.setup_request()
        first = self.app.actions.propose(self.profile["profile_id"], req)
        second = self.app.actions.propose(self.profile["profile_id"], req)
        def approve(p):
            return self.app.actions.decide(self.profile["profile_id"], p["preview"]["proposal_id"],
                "approve", p["preview_hash"], plan["state_version"])
        approve(first)
        with self.assertRaises(AppError) as ctx:
            approve(second)
        self.assertEqual(ctx.exception.code, "stale_state_version")
        self.assertEqual(len(self.app.actions.history(self.profile["profile_id"])), 1)

    def test_scoped_reschedule_undo_and_atomic_retry(self):
        from concurrent.futures import ThreadPoolExecutor
        from minder_app.plans import save_plan
        plan = self.make_plan()["plan"]
        plan["tasks"][0]["estimated_hours"] = 1
        plan["constraints"] = [dict(constraint_id="c", scope="weekly_hours", hard=True,
            value=10, unit="hours_per_week", evidence_id="user-report")]
        plan = save_plan(self.store, self.profile["profile_id"], plan, plan["state_version"])["plan"]
        old = plan["tasks"][0]["scheduled_at"]
        req = dict(kind="reschedule_task", target_id=plan["plan_id"], expected=plan["state_version"],
            diff=[dict(path="/tasks/synthetic-task/scheduled_at", before=old, after="2026-10-25T11:00:00Z")],
            reason="Explicit user reschedule")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.app.actions.direct(self.profile["profile_id"], req, "retry"), range(2)))
        self.assertEqual(results[0], results[1])
        undo = self.app.actions.undo(self.profile["profile_id"], results[0]["action"]["action_id"],
            results[0]["action"]["resulting_state_version"], "undo")
        self.assertEqual(undo["target"]["tasks"][0]["scheduled_at"], old)
