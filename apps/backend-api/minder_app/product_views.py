"""Read-only product compositions over A/C services and D's published operations.

No alternate scoring, state persistence or progress computation lives here.
"""
from .store import AppError
from .product_view_schemas import envelope, validate_view_request
from .product_state import state_view

VIEWS = ("overview", "career-match", "roadmap", "tasks", "progress", "news")
OPERATIONS = {(method, "/api/product/views/" + view)
              for method in ("GET", "POST") for view in VIEWS}


def career_read(app, profile, body):
    if profile is None:
        return {"status": "unavailable", "reason": "profile_required"}
    return app.services.public_context(app.services.career_context(
        profile, expected_profile_version=profile["version"],
        selected_role_ids=body.get("selected_role_ids"),
        selected_skill_ids=body.get("selected_skill_ids")))


def task_read(app, owner, body, snapshot=None):
    snapshot = snapshot if snapshot is not None else state_view(app.store, owner)
    plans = snapshot["plans"]
    if "plan_id" in body:
        # Resolve through the owner boundary even when the filtered list is empty.
        plans = [p for p in plans if p["plan_id"] == body["plan_id"]]
        if not plans:
            raise AppError("not_found", 404)
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
            operations = [] if task["locked"] or task["state"] == "cancelled" else (
                ["undo"] if task["state"] == "completed" else ["edit", "reschedule", "complete", "cancel"])
            tasks.append(dict(task=task, plan_id=plan["plan_id"],
                              state_version=plan["state_version"], supported_operations=operations,
                              action_validation="D checks current version, dependencies and feasibility on write"))
    tasks.sort(key=lambda item: (item["plan_id"], item["task"]["task_id"]))
    offset, limit = body.get("offset", 0), body.get("limit", 20)
    return dict(tasks=tasks[offset:offset + limit], total=len(tasks), offset=offset,
                next_offset=offset + limit if offset + limit < len(tasks) else None,
                plan_versions={p["plan_id"]: p["state_version"] for p in plans},
                order="plan_id,task_id", progress=snapshot["progress"])


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS:
        raise AppError("not_found", 404)
    validate_view_request(body)
    view = path.rsplit("/", 1)[-1]
    snapshot = state_view(app.store, owner)
    profile = snapshot["profile"]
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
        data = task_read(app, owner, body, snapshot)
    elif view == "progress":
        data = dict(snapshot["progress"],
                    progress_event_ids=snapshot["active_plan"]["progress_event_ids"] if snapshot["active_plan"] else [],
                    skill_evidence=profile["evidence"] if profile else [],
                    limitation="Event IDs are persisted activity references, not a detailed event history or skill assessment.")
    elif view == "roadmap":
        plans = snapshot["plans"]
        if "plan_id" in body:
            plans = [p for p in plans if p["plan_id"] == body["plan_id"]]
            if not plans:
                raise AppError("not_found", 404)
        data = dict(plans=plans, direction=snapshot["direction"], active_plan=snapshot["active_plan"],
                    skill_evidence=profile["evidence"] if profile else [],
                    requirements=[], unknowns=["Unknown competence is not a proven gap."],
                    gap_assessment_status="not_computed; use A career-match selected-role assessment")
        role_ids = list(dict.fromkeys(p["selected_role_id"] for p in plans))
        for role_id in role_ids:
            role = next((r for r in app.services.roles if r["role_id"] == role_id), None)
            if role:
                data["requirements"].append(dict(role=role,
                    limitation="Occupational ratings are not personal competence thresholds."))
            else:
                data["unknowns"].append("Requirements unavailable for " + role_id)
        status = "partial" if data["unknowns"][1:] else "available"
    elif view == "overview":
        active = snapshot["active_plan"]
        tasks = task_read(app, owner, dict(limit=50, **({"plan_id": active["plan_id"]} if active else {})), snapshot)
        next_task = None
        if active:
            by_id = {t["task_id"]: t for t in active["tasks"]}
            ordered = [by_id[tid] for tid in active["task_ids"]]
            from .plans import instant
            next_task = next((t for t in sorted(ordered, key=lambda t:
                instant(t["scheduled_at"]).timestamp() if t["scheduled_at"] else float("inf"))
                if t["state"] in ("proposed", "scheduled") and not t["locked"]
                and all(by_id[parent]["state"] == "completed" for parent in t["prerequisite_task_ids"])), None)
        from .product_content import resource_list
        data = dict(direction=snapshot["direction"], active_plan=active, tasks=tasks,
                    progress=snapshot["progress"], resources=resource_list(app, owner, {"limit": 3}, snapshot=snapshot),
                    pending_proposals=[p for p in app.actions.proposals(owner) if p["status"] == "pending"],
                    next_task=next_task,
                    next_task_order="Ready unlocked tasks from selected active plan; scheduled_at then plan task_ids order.")
    else:
        from .product_content import resource_list
        data = dict(resources=resource_list(app, owner, {}, snapshot=snapshot), market=career_read(app, profile, body),
                    news={"status": "unavailable", "reason": "No verified news feed integrated."})
        status = "partial"
    if profile is None:
        limitations.append("No profile saved; no personalized assessment is inferred.")
    return envelope(view, profile, data, limitations, status)
