"""Direct product edits over C's canonical profile/plan Store, never agent authority."""
import copy
import json
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, now, uid
from .plans import save_plan, complete_task
from .product_state_schemas import check

OPERATIONS = tuple((method, "/api/product/" + path) for method, path in (
    ("GET", "direction"), ("PUT", "direction"), ("POST", "tasks"),
    ("POST", "task-action"), ("GET", "progress")))


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def optional(store, owner, kind, identifier, db):
    try:
        return store.get(owner, kind, identifier, db=db)
    except AppError as error:
        if error.status != 404:
            raise
        return None


def progress(plan, *, observed_at=None):
    tasks = plan["tasks"] if plan else []
    eligible = [t for t in tasks if t["state"] != "cancelled"]
    completed = sum(t["state"] == "completed" for t in eligible)
    return dict(status="available" if eligible else "empty", plan_id=plan["plan_id"] if plan else None,
        state_version=plan["state_version"] if plan else None,
        completed_count=completed, eligible_count=len(eligible), cancelled_count=len(tasks)-len(eligible),
        fraction=completed/len(eligible) if eligible else None, observed_at=observed_at or now(),
        denominator="All non-cancelled tasks in the explicitly selected active plan, each task once. "
                    "Prerequisite links are dependencies, not parent/child rollups. Activity only, not skill readiness.")


def state_view(store, owner):
    """Read-only consistent snapshot for E: state_view(store, authenticated_owner)."""
    with store.connect() as db:
        db.execute("BEGIN")
        profile = optional(store, owner, "profile", owner, db)
        direction = optional(store, owner, "direction", owner, db)
        plans = [json.loads(r[0]) for r in db.execute(
            "SELECT body FROM documents WHERE owner=? AND kind='plan' ORDER BY id", (owner,))]
        active = next((p for p in plans if direction and p["plan_id"] == direction["plan_id"]), None)
        return dict(profile=profile, profile_version=profile["version"] if profile else None,
            direction=direction, plans=plans, active_plan=active, progress=progress(active))


def retry_write(app, owner, path, body, operation):
    store = app.store
    with store.transaction() as db:
        scope = encode(dict(path=path, body=body))
        old = db.execute("SELECT scope,result FROM product_requests WHERE owner=? AND key=?",
                         (owner, body["idempotency_key"])).fetchone()
        if old:
            if old["scope"] != scope:
                raise AppError("idempotency_scope_conflict", 409)
            return json.loads(old["result"])
        event_id = uid()
        result = operation(db, event_id)
        event = dict(event_id=event_id, path=path, request=body, created_at=now(), actor="explicit_user")
        db.execute("INSERT INTO product_events VALUES(?,?,?)", (owner, event_id, encode(event)))
        db.execute("INSERT INTO authorities VALUES(?,?,?,?)", (owner, event_id, scope, event["created_at"]))
        db.execute("INSERT INTO product_requests VALUES(?,?,?,?)",
                   (owner, body["idempotency_key"], scope, encode(result)))
        return result


def role_for(app, role_id):
    role = next((r for r in app.services.roles if r["role_id"] == role_id), None)
    if role is None:
        raise AppError("role_not_found", 404)
    return role


def validate_task_refs(app, task, profile):
    known = set(app.services.skill_entity_ids)
    known.update(e["subject_id"] for r in app.services.roles for e in r.get("requirements", []))
    if set(task.get("skill_ids", [])) - known:
        raise AppError("unknown_skill_reference")
    evidence = {e["evidence_id"] for e in profile["evidence"]}
    evidence.update(e["evidence_id"] for r in app.services.roles for e in r.get("requirements", []))
    if set(task["evidence_ids"]) - evidence:
        raise AppError("unknown_evidence_reference")
    if task.get("resource_id"):
        resource_for(task["resource_id"])


def resource_for(resource_id):
    from .resources import learning_options
    resource = next((r for r in learning_options()["resources"] if r["resource_id"] == resource_id), None)
    if resource is None:
        raise AppError("resource_not_found", 404)
    return resource


def direction_write(app, owner, body, db, event_id):
    store = app.store
    profile = store.get(owner, "profile", owner, db=db)
    role_for(app, body["role_id"])
    plan_id = body.get("plan_id")
    if plan_id:
        plan = store.get(owner, "plan", plan_id, db=db)
        if plan["selected_role_id"] != body["role_id"]:
            raise AppError("direction_plan_role_mismatch", 409)
    value = dict(role_id=body["role_id"], plan_id=plan_id, profile_version=profile["version"],
                 updated_at=now(), requirements_status="not_evaluated",
                 limitation="Direction selection does not certify readiness or generate preparation tasks.")
    return store.put(owner, "direction", owner, value, body["expected_version"], db=db)


def task_write(app, owner, body, db, event_id, *, create=False):
    store = app.store
    plan = store.get(owner, "plan", body["plan_id"], db=db)
    if plan["state_version"] != body["expected_state_version"]:
        raise AppError("stale_state_version", 409)
    undo = None
    if create:
        task = copy.deepcopy(body["task"])
        if task["state"] not in ("proposed", "scheduled") or task["activity_completion"] or task["mastery_verified"] or task["locked"]:
            raise AppError("new_task_requires_uncompleted_activity")
        validate_task_refs(app, task, store.get(owner, "profile", owner, db=db))
        if task["task_id"] in plan["task_ids"]:
            raise AppError("duplicate_task_id", 409)
        plan["tasks"].append(task)
        plan["task_ids"].append(task["task_id"])
    else:
        task = next((t for t in plan["tasks"] if t["task_id"] == body["task_id"]), None)
        if task is None:
            raise AppError("task_not_found", 404)
        if task["locked"]:
            raise AppError("task_locked", 409)
        operation = body["operation"]
        changes = body.get("changes", {})
        if operation in ("complete", "undo", "cancel") and changes:
            raise AppError("unexpected_task_changes")
        if operation == "complete":
            if task["state"] == "cancelled":
                raise AppError("invalid_task_transition", 409)
            if task["state"] == "completed":
                return dict(plan=plan, feasibility=dict(status="unchanged"))
            return complete_task(store, owner, plan["plan_id"], task["task_id"],
                                 plan["state_version"], event_id, db=db)
        if operation == "undo":
            if task["state"] != "completed":
                raise AppError("invalid_task_transition", 409)
            undo = task["task_id"]
            task.update(state="proposed", activity_completion=False)
        elif task["state"] in ("completed", "cancelled"):
            raise AppError("invalid_task_transition", 409)
        elif operation == "cancel":
            if any(task["task_id"] in t["prerequisite_task_ids"] and t["state"] != "cancelled" for t in plan["tasks"]):
                raise AppError("task_has_active_dependents", 409)
            task.update(state="cancelled", scheduled_at=None)
        elif operation == "edit":
            if not changes or set(changes) - {"title", "description", "estimated_hours"}:
                raise AppError("invalid_task_edit")
            task.update(changes)
        elif operation == "reschedule":
            if "scheduled_at" not in changes or set(changes) - {"scheduled_at", "estimated_hours"}:
                raise AppError("schedule_change_required")
            task.update(changes)
            task["state"] = "scheduled" if task["scheduled_at"] else "proposed"
        validate("Task", task)
    plan["progress_event_ids"].append(event_id)
    return save_plan(store, owner, plan, plan["state_version"], db=db, completion_undo=undo)


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS:
        raise AppError("product_capability_unavailable", 404)
    if method == "GET":
        view = state_view(app.store, owner)
        return view["progress"] if path.endswith("/progress") else dict(direction=view["direction"])
    from .product_migrations import migrate
    migrate(app.store)
    kind = "DirectionWrite" if path.endswith("/direction") else "TaskCreate" if path.endswith("/tasks") else "TaskAction"
    check(kind, body)
    def write(db, event_id):
        if kind == "DirectionWrite":
            return direction_write(app, owner, body, db, event_id)
        return task_write(app, owner, body, db, event_id, create=kind == "TaskCreate")
    return retry_write(app, owner, path, body, write)
