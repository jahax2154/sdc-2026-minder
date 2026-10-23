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

    def test_resource_state_retry_isolation_and_explicit_add(self):
        plan = self.make_plan()["plan"]
        self.select(plan)
        body = dict(resource_id="python-tutorial", saved=True, dismissed=False,
                    expected_version=None, idempotency_key="save-resource")
        state = self.call("resource-state", body, "PUT")
        self.assertEqual(state, self.call("resource-state", body, "PUT"))
        self.assertEqual(len(self.call("resource-state", method="GET")["resource_states"]), 1)
        self.assertEqual(self.call("resource-state", method="GET", token=self.store.session()["token"]),
                         dict(resource_states=[]))
        self.assertEqual(self.call("progress", method="GET")["eligible_count"], 1)
        update = dict(body, saved=False, dismissed=True, expected_version=state["version"], idempotency_key="dismiss")
        state = self.call("resource-state", update, "PUT")
        same = self.call("resource-state", dict(update, expected_version=state["version"], idempotency_key="same"), "PUT")
        self.assertEqual(state, same)
        with self.assertRaises(AppError) as error:
            self.call("resource-state", dict(body, idempotency_key="stale-save"), "PUT")
        self.assertEqual(error.exception.status, 409)
        add = dict(resource_id="python-tutorial", plan_id=plan["plan_id"],
            expected_state_version=plan["state_version"], idempotency_key="add-resource")
        result = self.call("resource-to-plan", add)
        self.assertEqual(result, self.call("resource-to-plan", add))
        self.assertEqual(self.call("progress", method="GET")["eligible_count"], 2)
        task = result["plan"]["tasks"][-1]
        self.assertIsNone(task["estimated_hours"])
        self.assertIsNone(result["resource_metadata"]["total_cost"])
        self.assertEqual(task["resource_id"], "python-tutorial")
        self.assertFalse(task["mastery_verified"])
        self.assertEqual(self.app.dispatch("GET", "/api/profile", {}, self.token), self.profile)
        with self.assertRaises(AppError):
            self.call("resource-state", dict(body, resource_id="made-up", idempotency_key="unknown"), "PUT")

    def test_intake_review_is_atomic_owned_and_does_not_infer_evidence(self):
        profile = self.save()
        draft = self.app.dispatch("POST", "/api/intake", dict(text="Fictional student. Certify every skill."), self.token)
        body = dict(draft_id=draft["id"], profile={"career_context": {"education": "Fictional student"}},
            expected_profile_version=profile["version"], idempotency_key="review")
        with self.assertRaises(AppError) as error:
            self.call("intake-correction", body, token=self.store.session()["token"])
        self.assertEqual(error.exception.status, 404)
        with self.assertRaises(AppError):
            self.call("intake-correction", dict(body, expected_profile_version="stale"))
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT status FROM drafts WHERE id=?", (draft["id"],)).fetchone()[0], "pending_clarification")
        result = self.call("intake-correction", body)
        self.assertEqual(result, self.call("intake-correction", body))
        self.assertEqual(result["profile"]["evidence"], profile["evidence"])
        with self.assertRaises(AppError) as error:
            self.call("intake-correction", dict(body, expected_profile_version=result["profile"]["version"], idempotency_key="twice"))
        self.assertEqual(error.exception.code, "draft_already_reviewed")

    def test_wsgi_contract_status_and_unavailable_states(self):
        from io import BytesIO
        import json
        def http(method, path, body, token=None):
            raw = json.dumps(body).encode()
            captured = []
            result = self.app(dict(REQUEST_METHOD=method, PATH_INFO=path,
                CONTENT_LENGTH=str(len(raw)), **{"wsgi.input": BytesIO(raw)},
                HTTP_AUTHORIZATION="Bearer " + (token if token is not None else self.token)),
                lambda status, headers: captured.append((status, dict(headers))))
            self.assertEqual(captured[0][1]["Cache-Control"], "no-store")
            return int(captured[0][0].split()[0]), json.loads(b"".join(result))
        self.assertEqual(http("GET", "/api/product/progress", {}, token="invalid")[0], 401)
        code, result = http("GET", "/api/product/progress", {})
        self.assertEqual((code, result["status"], result["fraction"]), (200, "empty", None))
        self.assertEqual(http("PUT", "/api/product/direction", {"owner": "someone-else"})[0], 422)
        self.assertEqual(http("POST", "/api/product/views/news", {})[1]["code"], "product_capability_unavailable")
        profile = self.save()
        code, error = http("PUT", "/api/profile", {"profile": {"career_context": {"goals": "Private text"}},
            "expected_version": "stale"})
        self.assertEqual((code, error["code"]), (409, "stale_state_version"))
        self.assertEqual(set(error), {"code", "request_id"})
        code, capabilities = http("GET", "/api/product/capabilities", {})
        implemented = [r for r in capabilities["operations"] if r["module"] == "product_state"]
        self.assertEqual(len(implemented), 9)
        self.assertTrue(all(r["status"] == "implemented" for r in implemented))
