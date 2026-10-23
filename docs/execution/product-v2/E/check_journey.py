"""Actual local-source E read journey; fictional user, disposable E-only DB."""
import json
from pathlib import Path
import tempfile
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.integration_cli import wsgi_request
from minder_ml.intelligence.policy import ROOT


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", action="store_true", help="Write sanitized fictional-user response examples in E docs")
    args = parser.parse_args()
    target = ROOT / "ml/artifacts/session-e/product"
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="read-journey-", dir=target) as folder:
        app, _ = build("E", database=Path(folder) / "runtime.sqlite3")
        token = ""
        def request(method, path, body=None):
            status, value = wsgi_request(app, method, path, body, token)
            assert status == 200, (path, status, value)
            return value
        token = request("POST", "/api/session")["token"]
        absent = request("POST", "/api/product/views/career-match")
        assert absent["status"] == "unavailable"
        profile = request("PUT", "/api/profile", {"profile": {"synthetic": True}})
        role_id = app.services.roles[0]["role_id"]
        context = request("POST", "/api/product/views/career-match", {"selected_role_ids": [role_id]})
        direct = request("POST", "/api/career-context", {"selected_role_ids": [role_id]})
        assert context["data"]["recommendation"] == direct["recommendation"]
        assert context["profile_version"] == profile["version"]
        assert "internal" not in context["data"]
        forecasts = [s for s in context["data"]["statements"] if s.get("kind") == "forecast"]
        assert forecasts and all(s["status"] == "unavailable" for s in forecasts)
        empty_progress = request("GET", "/api/product/views/progress")
        public_resources = request("POST", "/api/product/resources", {"topic_ids": ["source-term:python"]})
        plan = dict(plan_id="draft", profile_id=profile["profile_id"], selected_role_id=role_id,
            state_version="draft", previous_version=None, task_ids=[], tasks=[], progress_event_ids=[], constraints=[])
        plan = request("POST", "/api/plans", dict(plan=plan, idempotency_key="plan"))["plan"]
        request("PUT", "/api/product/direction", dict(role_id=role_id, plan_id=plan["plan_id"],
            expected_version=None, idempotency_key="direction"))
        created = request("POST", "/api/product/resource-to-plan", dict(resource_id="python-tutorial",
            plan_id=plan["plan_id"], expected_state_version=plan["state_version"], idempotency_key="add"))
        before = request("GET", "/api/product/views/overview")
        assert before["data"]["next_task"]["task_id"] == created["task_id"]
        request("POST", "/api/product/task-action", dict(plan_id=plan["plan_id"], task_id=created["task_id"],
            expected_state_version=created["plan"]["state_version"], operation="complete", idempotency_key="complete"))
        progress = request("GET", "/api/product/views/progress")
        assert progress["data"]["fraction"] == 1
        assert request("POST", "/api/product/views/tasks", {"state": "proposed"})["data"]["progress"]["fraction"] == 1
        assert request("GET", "/api/product/views/overview")["data"]["next_task"] is None
        request("PUT", "/api/product/resource-state", dict(resource_id="python-tutorial", saved=True,
            dismissed=False, expected_version=None, idempotency_key="save"))
        resources = request("POST", "/api/product/resources", {"saved": True})
        assert resources["total"] == 1
        assert resources["resources"][0]["resource_id"] == "python-tutorial"
        roadmap = request("GET", "/api/product/views/roadmap")
        assert roadmap["data"]["active_plan"]["state_version"] == progress["data"]["state_version"]
        assert request("GET", "/api/profile")["evidence"] == []
        request("GET", "/api/product/views/news")
        if args.examples:
            from jsonschema import validate
            schema = json.loads((ROOT / "docs/execution/product-v2/contracts.schema.json").read_text())
            for example in (absent, context, empty_progress):
                validate(example, schema["$defs"]["ProductView"])
            output = dict(synthetic_user=True, provider_calls=0, source_mode="actual existing catalogue and source library",
                examples={"absent_profile_career_match": absent, "selected_role_career_match": context,
                          "no_direction_progress": empty_progress, "python_resource_filter": public_resources})
            (ROOT / "docs/execution/product-v2/E/RESPONSE_EXAMPLES.json").write_text(json.dumps(output, indent=2) + "\n")
        print(json.dumps(dict(status="passed", transport="actual WSGI; no TCP listener", lane="E",
            catalogue_roles=len(app.services.roles), provider_calls=0, external_fetches=0,
            dependencies=dict(D="1cb81b1574e1ef263a47e3bb0e098c50482340c5"),
            checks=["all_six_views", "A_recommendation_unchanged", "forecast_unavailable", "no_internal_matrix",
                    "selected_plan_next_task", "canonical_progress_after_completion", "filtered_tasks_keep_progress",
                    "saved_resource_filter", "roadmap_version_agreement", "no_skill_mastery_inference"])))


if __name__ == "__main__":
    main()
