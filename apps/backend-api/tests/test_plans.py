import copy
from support import AppCase, fixture
from minder_app.plans import check_plan, complete_task, save_plan
from minder_app.store import AppError


class PlanTests(AppCase):
    def test_other_saved_plan_cannot_double_book_availability(self):
        profile = self.save()
        profile["constraints"] = [dict(constraint_id="h", scope="weekly_hours", hard=True,
            value=5, unit="hours_per_week", evidence_id="explicit-user-hours")]
        profile = self.app.dispatch("PUT", "/api/profile", dict(profile=profile,
            expected_version=profile["version"]), self.token)
        plan = fixture("plan_progress")
        plan["tasks"][0]["estimated_hours"] = 1
        self.app.dispatch("POST", "/api/plans", dict(plan=plan, idempotency_key="p1"), self.token)
        with self.assertRaises(AppError) as ctx:
            self.app.dispatch("POST", "/api/plans", dict(plan=plan, idempotency_key="p2"), self.token)
        self.assertEqual(ctx.exception.code, "schedule_overlap")
        self.assertEqual(len(self.store.list(profile["profile_id"], "plan")), 1)

    def test_unknown_effort_and_persistent_completion(self):
        result = self.make_plan()
        self.assertEqual(result["feasibility"]["status"], "unknown")
        plan = result["plan"]
        result = complete_task(self.store, self.profile["profile_id"], plan["plan_id"],
            "synthetic-task", plan["state_version"], "explicit-request-test")
        task = result["plan"]["tasks"][0]
        self.assertTrue(task["activity_completion"])
        self.assertFalse(task["mastery_verified"])
        self.assertEqual(result["plan"]["progress_event_ids"], ["explicit-request-test"])
        edited = copy.deepcopy(result["plan"])
        edited["tasks"] = []; edited["task_ids"] = []
        with self.assertRaises(AppError):
            save_plan(self.store, self.profile["profile_id"], edited, edited["state_version"])

    def test_cycle_lock_capacity_and_overlap(self):
        plan = self.make_plan()["plan"]
        plan["tasks"][0]["prerequisite_task_ids"] = ["synthetic-task"]
        with self.assertRaises(AppError):
            check_plan(plan, self.profile)
        plan["tasks"][0]["prerequisite_task_ids"] = []
        plan["tasks"][0]["estimated_hours"] = 3
        plan["constraints"] = [dict(constraint_id="c", scope="weekly_hours", hard=True,
                                    value=2, unit="hours_per_week", evidence_id="user-hours")]
        with self.assertRaises(AppError) as ctx:
            check_plan(plan, self.profile)
        self.assertEqual(ctx.exception.code, "weekly_capacity_conflict")
        plan["constraints"][0]["value"] = 10
        second = copy.deepcopy(plan["tasks"][0]); second["task_id"] = "second"
        plan["tasks"].append(second); plan["task_ids"].append("second")
        with self.assertRaises(AppError) as ctx:
            check_plan(plan, self.profile)
        self.assertEqual(ctx.exception.code, "schedule_overlap")
