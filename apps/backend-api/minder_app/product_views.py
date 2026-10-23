"""Read-only product compositions over A/C services and D's published operations.

No alternate scoring, state persistence or progress computation lives here.
"""
from .store import AppError
from .product_view_schemas import envelope, validate_view_request

VIEWS = ("overview", "career-match", "roadmap", "tasks", "progress", "news")
OPERATIONS = {(method, "/api/product/views/" + view)
              for method in ("GET", "POST") for view in VIEWS}


def optional_document(store, owner, kind, doc_id):
    try:
        return store.get(owner, kind, doc_id)
    except AppError as error:
        if error.code == "not_found" and error.status == 404:
            return None
        raise


def state_read(app, owner, name):
    """Only consume advertised D operations; errors never become fixture state."""
    from .product_routes import module_for
    module = module_for("product_state")
    operation = ("GET", "/api/product/" + name)
    if module is None or operation not in getattr(module, "OPERATIONS", ()):
        return {"status": "unavailable", "reason": "D operation not integrated: " + name}
    return module.dispatch(app, owner, *operation, {})


def career_read(app, profile, body):
    if profile is None:
        return {"status": "unavailable", "reason": "profile_required"}
    return app.services.public_context(app.services.career_context(
        profile, expected_profile_version=profile["version"],
        selected_role_ids=body.get("selected_role_ids"),
        selected_skill_ids=body.get("selected_skill_ids")))


def task_read(app, owner, body):
    plans = app.store.list(owner, "plan")
    if "plan_id" in body:
        # Resolve through the owner boundary even when the filtered list is empty.
        plans = [app.store.get(owner, "plan", body["plan_id"])]
    tasks = []
    from .plans import instant
    lower = instant(body["scheduled_from"]) if "scheduled_from" in body else None
    upper = instant(body["scheduled_to"]) if "scheduled_to" in body else None
    if lower and upper and lower > upper:
        raise AppError("invalid_schedule_range")
    for plan in plans:
        for task in plan["tasks"]:
            if body.get("state") and task["state"] != body["state"]:
                continue
            scheduled = instant(task["scheduled_at"]) if task["scheduled_at"] else None
            if lower and (scheduled is None or scheduled < lower):
                continue
            if upper and (scheduled is None or scheduled > upper):
                continue
            tasks.append(dict(task=task, plan_id=plan["plan_id"],
                              state_version=plan["state_version"]))
    tasks.sort(key=lambda item: (item["plan_id"], item["task"]["task_id"]))
    offset, limit = body.get("offset", 0), body.get("limit", 20)
    return dict(tasks=tasks[offset:offset + limit], total=len(tasks), offset=offset,
                next_offset=offset + limit if offset + limit < len(tasks) else None,
                plan_versions={p["plan_id"]: p["state_version"] for p in plans},
                order="plan_id,task_id", progress=state_read(app, owner, "progress"))


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS:
        raise AppError("not_found", 404)
    validate_view_request(body)
    view = path.rsplit("/", 1)[-1]
    profile = optional_document(app.store, owner, "profile", owner)
    limitations = []
    status = "available"
    if view == "career-match":
        data = career_read(app, profile, body)
        if profile is None or data.get("recommendation") is None:
            status = "unavailable"
        elif data["recommendation"].get("status") != "available":
            status = "partial"
        limitations += data.get("limitations", [])
    elif view == "tasks":
        data = task_read(app, owner, body)
    elif view == "progress":
        data = state_read(app, owner, "progress")
        if data.get("status") == "unavailable":
            status = "unavailable"
    elif view == "roadmap":
        plans = app.store.list(owner, "plan")
        if "plan_id" in body:
            plans = [app.store.get(owner, "plan", body["plan_id"])]
        data = dict(plans=plans, direction=state_read(app, owner, "direction"),
                    skill_evidence=profile["evidence"] if profile else [],
                    requirements=[], unknowns=["Unknown competence is not a proven gap."])
        role_ids = list(dict.fromkeys(p["selected_role_id"] for p in plans))
        for role_id in role_ids:
            role = next((r for r in app.services.roles if r["role_id"] == role_id), None)
            if role:
                data["requirements"].append(dict(role=role,
                    limitation="Occupational ratings are not personal competence thresholds."))
            else:
                data["unknowns"].append("Requirements unavailable for " + role_id)
        status = "partial" if not plans or data["direction"].get("status") == "unavailable" else "available"
    elif view == "overview":
        tasks = task_read(app, owner, {"limit": 50})
        direction = state_read(app, owner, "direction")
        data = dict(direction=direction, tasks=tasks,
                    pending_proposals=[p for p in app.actions.proposals(owner) if p["status"] == "pending"],
                    next_task=None)
        # Do not guess which alternative plan the user selected.
        limitations.append("Next task requires a selected active plan and a supported task order.")
        status = "partial"
    else:
        from .product_content import resource_list
        data = dict(resources=resource_list(app, owner, {}), market=career_read(app, profile, body),
                    news={"status": "unavailable", "reason": "No verified news feed integrated."})
        status = "partial"
    if profile is None:
        limitations.append("No profile saved; no personalized assessment is inferred.")
    return envelope(view, profile, data, limitations, status)
