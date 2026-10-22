import copy
from test_profiles import ProfileTests, fixture
from minder_app.plans import check_plan, complete_task, save_plan
from minder_app.store import AppError


class PlanTests(ProfileTests):
    def make_plan(self):
        self.profile = self.save()
        plan = fixture("plan_progress")
        plan["profile_id"] = self.profile["profile_id"]
        return self.app.dispatch("POST", "/api/plans", dict(plan=plan, idempotency_key="create-1"), self.token)

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
