"""Versioned task graph and deterministic feasibility; no fit scoring."""
import copy
from datetime import datetime, timedelta
import json
from zoneinfo import ZoneInfo
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, uid, now


def instant(value):
    point = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if point.tzinfo is None:
        raise AppError("timezone_required")
    return point


def check_plan(plan, profile, previous=None, *, completion_undo=None):
    validate("PlanProgress", plan)
    if plan["profile_id"] != profile["profile_id"]:
        raise AppError("profile_plan_identity_mismatch")
    tasks = {t["task_id"]: t for t in plan["tasks"]}
    if plan["task_ids"] != [t["task_id"] for t in plan["tasks"]]:
        raise AppError("task_index_inconsistent")
    if len(tasks) != len(plan["tasks"]):
        raise AppError("duplicate_task_id")
    visiting, visited = set(), set()
    def visit(task_id):
        if task_id not in tasks:
            raise AppError("missing_prerequisite")
        if task_id in visiting:
            raise AppError("cyclic_prerequisites")
        if task_id in visited:
            return
        visiting.add(task_id)
        for parent in tasks[task_id]["prerequisite_task_ids"]:
            visit(parent)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in tasks:
        visit(task_id)
    if previous:
        if previous["selected_role_id"] != plan["selected_role_id"]:
            raise AppError("new_role_requires_separate_plan")
        for old in previous["tasks"]:
            undo = (old["task_id"] == completion_undo and not old["locked"]
                    and old["state"] == "completed"
                    and tasks.get(old["task_id"]) == dict(old, state="proposed", activity_completion=False))
            if (old["locked"] or old["state"] == "completed") and tasks.get(old["task_id"]) != old and not undo:
                raise AppError("completed_or_locked_task_preserved")
        if not set(previous["progress_event_ids"]).issubset(plan["progress_event_ids"]):
            raise AppError("progress_history_preserved")
    capacity = None
    deadlines = {}
    for constraint in profile["constraints"] + plan["constraints"]:
        if constraint["scope"] == "weekly_hours":
            value = constraint["value"]
            if (not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 168
                    or constraint["unit"] != "hours_per_week"):
                raise AppError("invalid_weekly_capacity")
            capacity = min(capacity, value) if capacity is not None else value
        elif constraint["scope"].startswith("deadline:"):
            deadlines[constraint["scope"][9:]] = instant(constraint["value"])
        elif constraint["hard"] and any(t["scheduled_at"] for t in tasks.values() if t["state"] == "scheduled"):
            raise AppError("unsupported_hard_constraint_requires_clarification")
    slots, weekly = [], {}
    unknown = []
    for task in tasks.values():
        if task["activity_completion"] != (task["state"] == "completed"):
            raise AppError("completion_state_inconsistent")
        if task["mastery_verified"] and (not previous or not any(
                t["task_id"] == task["task_id"] and t["mastery_verified"] for t in previous["tasks"])):
            raise AppError("activity_cannot_certify_mastery")
        if task["state"] == "completed":
            if any(tasks[p]["state"] != "completed" for p in task["prerequisite_task_ids"]):
                raise AppError("prerequisite_not_completed")
        if task["state"] != "scheduled":
            continue
        if task["scheduled_at"] is None or task["estimated_hours"] is None or capacity is None:
            unknown.append(task["task_id"])
            continue
        start = instant(task["scheduled_at"])
        end = start + timedelta(hours=task["estimated_hours"])
        if task["task_id"] in deadlines and end > deadlines[task["task_id"]]:
            raise AppError("firm_deadline_conflict", 409)
        for parent_id in task["prerequisite_task_ids"]:
            parent = tasks[parent_id]
            if parent["state"] == "completed":
                continue
            if parent["scheduled_at"] is None or parent["estimated_hours"] is None or parent["state"] != "scheduled":
                raise AppError("prerequisite_schedule_unknown", 409)
            if instant(parent["scheduled_at"]) + timedelta(hours=parent["estimated_hours"]) > start:
                raise AppError("prerequisite_schedule_conflict", 409)
        if any(start < b and end > a for a, b in slots):
            raise AppError("schedule_overlap", 409)
        slots.append((start, end))
        # Split across local calendar days so week boundaries cannot hide overbooking.
        cursor = start.astimezone(ZoneInfo(profile["timezone"]))
        finish = end.astimezone(ZoneInfo(profile["timezone"]))
        if (finish - cursor).total_seconds() > 168 * 3600:
            raise AppError("task_effort_exceeds_week")
        while cursor < finish:
            boundary = (cursor + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            stop = min(boundary, finish)
            key = tuple(cursor.isocalendar()[:2])
            weekly[key] = weekly.get(key, 0) + (stop - cursor).total_seconds() / 3600
            cursor = stop
    if any(h > capacity for h in weekly.values()) if capacity is not None else False:
        raise AppError("weekly_capacity_conflict", 409)
    return {"status": "unknown" if unknown else "checked", "unknown_effort_or_capacity_tasks": unknown}


def save_plan(store, owner, plan, expected=None, *, db=None, completion_undo=None):
    if db is None:
        with store.transaction() as conn:
            return save_plan(store, owner, plan, expected, db=conn, completion_undo=completion_undo)
    profile = store.get(owner, "profile", owner, db=db)
    previous = store.get(owner, "plan", plan["plan_id"], db=db) if expected else None
    feasibility = check_plan(plan, profile, previous, completion_undo=completion_undo)
    others = [json.loads(row[0]) for row in db.execute(
        "SELECT body FROM documents WHERE owner=? AND kind='plan' AND id<>?", (owner, plan["plan_id"]))]
    scheduled_others = [p for p in others if any(t["state"] == "scheduled" for t in p["tasks"])]
    if scheduled_others and any(t["state"] == "scheduled" for t in plan["tasks"]):
        # Availability is per person. Alternative plans explicitly saved by the
        # user cannot quietly double-book one another.
        aggregate = copy.deepcopy(plan)
        aggregate.update(tasks=[], task_ids=[], constraints=[])
        for item in scheduled_others + [plan]:
            for task in item["tasks"]:
                task = copy.deepcopy(task)
                task["task_id"] = item["plan_id"] + ":" + task["task_id"]
                task["prerequisite_task_ids"] = [item["plan_id"] + ":" + p for p in task["prerequisite_task_ids"]]
                aggregate["tasks"].append(task)
                aggregate["task_ids"].append(task["task_id"])
        combined = check_plan(aggregate, profile)
        if combined["status"] == "unknown":
            raise AppError("combined_plan_availability_unknown", 409)
    saved = store.put(owner, "plan", plan["plan_id"], plan, expected, db=db)
    return {"plan": saved, "feasibility": feasibility}


def complete_task(store, owner, plan_id, task_id, expected, request_id, *, db=None):
    if db is None:
        with store.transaction() as conn:
            return complete_task(store, owner, plan_id, task_id, expected, request_id, db=conn)
    plan = store.get(owner, "plan", plan_id, db=db)
    task = next((t for t in plan["tasks"] if t["task_id"] == task_id), None)
    if task is None:
        raise AppError("task_not_found", 404)
    if task["locked"]:
        raise AppError("task_locked", 409)
    task.update(state="completed", activity_completion=True)  # mastery unchanged
    plan["progress_event_ids"].append(request_id)
    return save_plan(store, owner, plan, expected, db=db)


def create_plan(store, owner, plan, idempotency_key, design=None):
    """Direct structured UI request. Retries cannot duplicate plan creation."""
    if not idempotency_key or len(idempotency_key) > 200:
        raise AppError("idempotency_key_required")
    with store.transaction() as db:
        db.execute("CREATE TABLE IF NOT EXISTS plan_creations(owner TEXT, key TEXT, body TEXT, "
                   "result TEXT, PRIMARY KEY(owner,key))")
        encoded = json.dumps(dict(plan=plan, design=design), sort_keys=True)
        old = db.execute("SELECT body,result FROM plan_creations WHERE owner=? AND key=?",
                         (owner, idempotency_key)).fetchone()
        if old:
            if old["body"] != encoded:
                raise AppError("idempotency_scope_conflict", 409)
            return json.loads(old["result"])
        plan = copy.deepcopy(plan)
        plan.update(plan_id=uid(), profile_id=owner, state_version=uid(), previous_version=None)
        db.execute("INSERT INTO authorities VALUES(?,?,?,?)", (owner, uid(),
            json.dumps(dict(kind="explicit_plan_create", idempotency_key=idempotency_key, plan=plan), sort_keys=True), now()))
        result = save_plan(store, owner, plan, db=db)
        if design is not None:
            store.put(owner, "plan_design", plan["plan_id"], dict(design=design, plan_id=plan["plan_id"]), None, db=db)
        db.execute("INSERT INTO plan_creations VALUES(?,?,?,?)", (
            owner, idempotency_key, encoded, json.dumps(result)))
        return result
