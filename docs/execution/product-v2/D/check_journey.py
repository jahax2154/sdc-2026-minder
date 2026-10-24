"""Real local-source WSGI journey; fictional profile, disposable D-only database."""
import json
from pathlib import Path
import tempfile
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.integration_cli import wsgi_request
from minder_ml.intelligence.policy import ROOT
from minder_app.api import Application
from minder_app.store import Store


def main():
    target = ROOT / "ml/artifacts/session-d/product"
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="journey-", dir=target) as folder:
        database = Path(folder) / "runtime.sqlite3"
        app, _ = build("D", database=database)
        token = ""
        def request(method, path, body=None):
            code, value = wsgi_request(app, method, path, body, token)
            assert code == 200, (method, path, code, value)
            return value
        session = request("POST", "/api/session")
        token = session["token"]
        profile = request("PUT", "/api/profile", {"profile": {
            "synthetic": True, "career_context": {"education": "Fictional journey check"}}})
        role = app.services.roles[0]["role_id"]
        plan = dict(plan_id="draft", profile_id=session["profile_id"], selected_role_id=role,
            state_version="draft", previous_version=None, task_ids=[], tasks=[], progress_event_ids=[], constraints=[])
        plan = request("POST", "/api/plans", dict(plan=plan, idempotency_key="plan"))["plan"]
        request("PUT", "/api/product/direction", dict(role_id=role, plan_id=plan["plan_id"],
            expected_version=None, idempotency_key="select"))
        assert request("GET", "/api/product/progress")["fraction"] is None
        add = dict(resource_id="python-tutorial", plan_id=plan["plan_id"],
            expected_state_version=plan["state_version"], idempotency_key="add")
        created = request("POST", "/api/product/resource-to-plan", add)
        assert request("POST", "/api/product/resource-to-plan", add) == created
        plan = created["plan"]
        completed = request("POST", "/api/product/task-action", dict(plan_id=plan["plan_id"],
            task_id=created["task_id"], expected_state_version=plan["state_version"],
            operation="complete", idempotency_key="complete"))
        assert request("GET", "/api/product/progress")["fraction"] == 1
        app = Application(Store(database), services=app.services)
        assert request("GET", "/api/product/progress")["fraction"] == 1
        plan = completed["plan"]
        request("POST", "/api/product/task-action", dict(plan_id=plan["plan_id"],
            task_id=created["task_id"], expected_state_version=plan["state_version"],
            operation="undo", idempotency_key="undo"))
        assert request("GET", "/api/product/progress")["fraction"] == 0
        assert request("GET", "/api/profile")["evidence"] == profile["evidence"] == []
        print(json.dumps(dict(status="passed", transport="WSGI, no TCP listener", lane="D",
            catalogue_roles=len(app.services.roles), selected_role_id=role, profile="fictional",
            checks=["partial_profile", "explicit_plan_selection", "empty_progress", "resource_add_retry",
                    "complete", "restart_refetch", "undo", "no_mastery_inference"], provider_calls=0)))


if __name__ == "__main__":
    main()
