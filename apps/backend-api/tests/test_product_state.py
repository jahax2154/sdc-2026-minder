import copy
from types import SimpleNamespace
from support import AppCase, fixture
from minder_app.store import AppError, Store
from minder_app.api import Application
from minder_app.product_state import state_view


class ProductStateTests(AppCase):
    def setUp(self):
        super().setUp()
        self.app.services.roles = [dict(role_id="synthetic-role", requirements=[]),
                                   dict(role_id="other-role", requirements=[])]

    def call(self, name, body=None, method="POST", token=None):
        return self.app.dispatch(method, "/api/product/" + name, body or {}, token or self.token)

    def select(self, plan):
        return self.call("direction", dict(role_id=plan["selected_role_id"], plan_id=plan["plan_id"],
            expected_version=None, idempotency_key="select"), "PUT")

    def action(self, plan, operation, key=None, **extra):
        return self.call("task-action", dict(plan_id=plan["plan_id"], task_id="synthetic-task",
            operation=operation, expected_state_version=plan["state_version"],
            idempotency_key=key or operation, **extra))

    def test_direction_empty_replace_and_history(self):
        self.assertEqual(self.call("progress", method="GET")["status"], "empty")
        plan = self.make_plan()["plan"]
        selected = self.select(plan)
        self.assertEqual(self.select(plan), selected)
        self.assertEqual(len(self.store.list(self.profile["profile_id"], "plan")), 1)
        self.call("direction", dict(role_id="other-role", expected_version=selected["version"],
            idempotency_key="switch"), "PUT")
        self.assertEqual(self.call("progress", method="GET")["eligible_count"], 0)
        self.assertEqual(len(state_view(self.store, self.profile["profile_id"])["plans"]), 1)

    def test_complete_retry_undo_and_restart_share_agent_records(self):
        plan = self.make_plan()["plan"]
        self.select(plan)
        result = self.action(plan, "complete")
        self.assertEqual(result, self.action(plan, "complete"))
        self.assertEqual(self.call("progress", method="GET")["fraction"], 1)
        self.assertFalse(result["plan"]["tasks"][0]["mastery_verified"])
        plan = self.action(result["plan"], "undo")["plan"]
        self.assertEqual(len(plan["progress_event_ids"]), 2)
        self.assertEqual(state_view(Store(self.store.path), self.profile["profile_id"])["progress"]["fraction"], 0)
        # C's executor consumes the same version/plan, without a state bridge.
        request = dict(kind="complete_task", target_id=plan["plan_id"], expected=plan["state_version"],
            diff=[dict(path="/tasks/synthetic-task/state", before="proposed", after="completed")],
            reason="Explicit fixture completion", evidence_ids=[])
        self.app.actions.direct(self.profile["profile_id"], request, "agent-direct")
        self.assertEqual(self.call("progress", method="GET")["fraction"], 1)
        with self.assertRaises(AppError) as error:
            self.action(plan, "edit", changes={"title": "Stale"})
        self.assertEqual(error.exception.status, 409)

    def test_create_edit_cancel_denominator_and_retry_scope(self):
        plan = self.make_plan()["plan"]
        self.select(plan)
        task = dict(fixture("plan_progress")["tasks"][0], task_id="manual", state="proposed",
                    scheduled_at=None, title="Fictional practice", skill_ids=[])
        body = dict(plan_id=plan["plan_id"], expected_state_version=plan["state_version"],
                    idempotency_key="new", task=task)
        result = self.call("tasks", body)
        self.assertEqual(result, self.call("tasks", body))
        self.assertEqual(self.call("progress", method="GET")["eligible_count"], 2)
        with self.assertRaises(AppError):
            self.call("tasks", dict(body, task=dict(task, title="Different scope")))
        result = self.action(result["plan"], "edit", changes={"title": "Updated"})
        result = self.action(result["plan"], "cancel")
        progress = self.call("progress", method="GET")
        self.assertEqual((progress["eligible_count"], progress["cancelled_count"]), (1, 1))

    def test_ownership_invalid_role_and_refs(self):
        plan = self.make_plan()["plan"]
        other = self.store.session()["token"]
        with self.assertRaises(AppError) as error:
            self.call("task-action", dict(plan_id=plan["plan_id"], task_id="synthetic-task", operation="complete",
                expected_state_version=plan["state_version"], idempotency_key="x"), token=other)
        self.assertEqual(error.exception.status, 404)
        with self.assertRaises(AppError):
            self.call("direction", dict(role_id="invalid", expected_version=None, idempotency_key="bad"), "PUT")
        body = dict(plan_id=plan["plan_id"], expected_state_version=plan["state_version"],
            idempotency_key="bad-ref", task=dict(plan["tasks"][0], task_id="new", skill_ids=["unknown"]))
        with self.assertRaises(AppError):
            self.call("tasks", body)
        self.assertEqual(self.store.get(self.profile["profile_id"], "plan", plan["plan_id"]), plan)

    def test_schedule_conflict_and_completed_dependency_undo(self):
        plan = self.make_plan()["plan"]
        result = self.action(plan, "reschedule", changes={"scheduled_at": None})
        self.assertEqual(result["plan"]["tasks"][0]["state"], "proposed")
        result = self.action(result["plan"], "complete")
        task = dict(result["plan"]["tasks"][0], task_id="child", state="proposed", activity_completion=False,
                    prerequisite_task_ids=["synthetic-task"])
        result = self.call("tasks", dict(plan_id=plan["plan_id"], expected_state_version=result["plan"]["state_version"],
            idempotency_key="child", task=task))
        result = self.call("task-action", dict(plan_id=plan["plan_id"], task_id="child", operation="complete",
            expected_state_version=result["plan"]["state_version"], idempotency_key="complete-child"))
        with self.assertRaises(AppError) as error:
            self.action(result["plan"], "undo")
        self.assertEqual(error.exception.code, "prerequisite_not_completed")
