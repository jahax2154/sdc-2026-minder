"""Trusted scoped requests and immutable proposals, enforced inside SQLite writes.

LLM-supplied origin/approval/request IDs are never trusted. HTTP UI instructions
mint direct authorities here; workers may only prepare pending proposals.
"""
import copy
import hashlib
import json
from contextlib import contextmanager
from minder_ml.intelligence.service_contracts import validate
from .plans import save_plan, instant
from .store import AppError, uid, now


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def migrate(store):
    with store.transaction() as db:
        db.execute("CREATE TABLE IF NOT EXISTS authorities(owner TEXT, id TEXT, scope TEXT, "
                   "created_at TEXT, PRIMARY KEY(owner,id))")
        db.execute("CREATE TABLE IF NOT EXISTS proposals(owner TEXT, id TEXT, preview TEXT, "
                   "hash TEXT, status TEXT, PRIMARY KEY(owner,id))")
        db.execute("CREATE TABLE IF NOT EXISTS executions(owner TEXT, key TEXT, scope TEXT, "
                   "result TEXT, PRIMARY KEY(owner,key))")
        db.execute("CREATE TABLE IF NOT EXISTS action_audit(owner TEXT, id TEXT, body TEXT, "
                   "PRIMARY KEY(owner,id))")
        db.execute("INSERT OR IGNORE INTO migrations VALUES(2)")


def action_request(kind, target_id, expected, diff, reason, evidence_ids=()):
    if kind not in ("complete_task", "reschedule_task", "update_profile", "change_goal", "replace_plan",
                    "create_task", "edit_task", "schedule_task", "configure_automation"):
        raise AppError("unsupported_action")
    if not expected or not target_id or not diff:
        raise AppError("specific_action_scope_required")
    for change in diff:
        validate("ActionDiff", change)
    if len({c["path"] for c in diff}) != len(diff):
        raise AppError("duplicate_diff_path")
    return dict(kind=kind, target_id=target_id, expected_state_version=expected,
                diff=copy.deepcopy(diff), reason=reason, evidence_ids=list(evidence_ids))


class _TransactionStore:
    """Reuse D's validated writer on the executor's existing transaction."""
    def __init__(self, store, db):
        self.store, self.db = store, db

    def __getattr__(self, name):
        return getattr(self.store, name)

    @contextmanager
    def transaction(self):
        yield self.db


def _automation_changes(before, request):
    changes={}
    for change in request['diff']:
        parts=change['path'].split('/')
        if len(parts)!=3 or parts[1]!='settings' or parts[2] not in ('enabled','check_time','timezone','state','scope'):
            raise AppError('unsupported_automation_scope')
        field=parts[2]
        if before.get(field)!=change['before']:
            raise AppError('diff_before_mismatch',409)
        changes[field]=change['after']
    return changes


class ActionExecutor:
    def __init__(self, store):
        self.store = store
        migrate(store)
        from .agents import migrate as migrate_agents
        migrate_agents(store)

    def direct(self, owner, request, idempotency_key):
        """Called ONLY from an authenticated structured user-command route."""
        request = action_request(**request)
        with self.store.transaction() as db:
            existing = self._retry(db, owner, idempotency_key, request)
            if existing is not None:
                return existing
            rid = uid()
            db.execute("INSERT INTO authorities VALUES(?,?,?,?)", (owner, rid, encode(request), now()))
            return self._execute(db, owner, request, idempotency_key, request_id=rid)

    def propose(self, owner, request, *, origin="inferred", db=None):
        if db is None:
            with self.store.transaction() as conn:
                return self.propose(owner, request, origin=origin, db=conn)
        if origin not in ("inferred", "scheduled", "market_event"):
            raise AppError("proposal_origin_invalid")
        request = action_request(**request)
        # Validate preview against current state, without writing the target.
        self._preview(db, owner, request)
        preview = dict(request=request, proposal_id=uid(), origin=origin)
        fingerprint = digest(preview)
        db.execute("INSERT INTO proposals VALUES(?,?,?,?,?)", (
            owner, preview["proposal_id"], encode(preview), fingerprint, "pending"))
        return dict(preview=preview, preview_hash=fingerprint, status="pending", target_changed=False)

    def decide(self, owner, proposal_id, decision, preview_hash, expected_state_version):
        with self.store.transaction() as db:
            row = db.execute("SELECT * FROM proposals WHERE owner=? AND id=?", (owner, proposal_id)).fetchone()
            if row is None:
                raise AppError("proposal_not_found", 404)
            preview = json.loads(row["preview"])
            req = preview["request"]
            if preview_hash != row["hash"] or expected_state_version != req["expected_state_version"]:
                raise AppError("approval_scope_mismatch", 409)
            if decision == "reject":
                if row["status"] not in ("pending", "rejected"):
                    raise AppError("proposal_already_applied", 409)
                db.execute("UPDATE proposals SET status='rejected' WHERE owner=? AND id=?", (owner, proposal_id))
                return dict(status="rejected", target_changed=False)
            if decision != "approve" or row["status"] == "rejected":
                raise AppError("explicit_proposal_decision_required", 409)
            key = "approval:" + proposal_id
            old = self._retry(db, owner, key, req)
            if old is not None:
                return old
            if row["status"] != "pending":
                raise AppError("proposal_not_pending", 409)
            result = self._execute(db, owner, req, key, proposal=preview)
            db.execute("UPDATE proposals SET status='applied' WHERE owner=? AND id=?", (owner, proposal_id))
            return result

    def proposals(self, owner):
        with self.store.connect() as db:
            return [dict(preview=json.loads(r["preview"]), preview_hash=r["hash"], status=r["status"])
                    for r in db.execute("SELECT * FROM proposals WHERE owner=? ORDER BY rowid", (owner,))]

    def history(self, owner):
        with self.store.connect() as db:
            return [json.loads(r[0]) for r in db.execute("SELECT body FROM action_audit WHERE owner=?", (owner,))]

    def _retry(self, db, owner, key, req):
        if not isinstance(key, str) or not key or len(key) > 200:
            raise AppError("idempotency_key_required")
        row = db.execute("SELECT scope,result FROM executions WHERE owner=? AND key=?", (owner, key)).fetchone()
        if row:
            if row["scope"] != encode(req):
                raise AppError("idempotency_scope_conflict", 409)
            return json.loads(row["result"])

    def _preview(self, db, owner, req):
        kind = ('agent_settings' if req['kind']=='configure_automation' else
                "profile" if req["kind"] in ("update_profile", "change_goal") else "plan")
        if kind in ('profile','agent_settings') and req["target_id"] != owner:
            raise AppError("profile_not_found", 404)
        try:
            before = self.store.get(owner, kind, req["target_id"], db=db)
        except AppError as error:
            if error.status!=404 or kind!='agent_settings':raise
            before={'version':'missing'}
        version_key = "state_version" if kind == 'plan' else 'version'
        if before[version_key] != req["expected_state_version"]:
            raise AppError("stale_state_version", 409)
        if kind=='agent_settings':
            from .automation_state import save_automation_settings
            changes=_automation_changes(before,req)
            # Validate through D's actual writer, then roll back every tentative
            # state/authority/event change. No provider or side effect in helper.
            db.execute('SAVEPOINT automation_preview')
            try:
                after=save_automation_settings(_TransactionStore(self.store,db),owner,changes,
                    None if before['version']=='missing' else before['version'])
            finally:
                db.execute('ROLLBACK TO automation_preview')
                db.execute('RELEASE automation_preview')
            return kind,before,after
        after = copy.deepcopy(before)
        for change in req["diff"]:
            parts = change["path"].split("/")
            if kind == 'plan' and req['kind'] == 'create_task' and len(parts) == 3 and parts[1] == 'tasks':
                task = copy.deepcopy(change['after'])
                validate('Task', task)
                if (change['before'] is not None or task['task_id'] != parts[2]
                        or task['task_id'] in after['task_ids'] or task['state'] != 'proposed'
                        or task['scheduled_at'] is not None or task['mastery_verified'] or task['activity_completion']
                        or task['locked'] or task['evidence_ids'] or task.get('skill_ids') or task.get('resource_id')):
                    raise AppError('generated_task_scope_invalid')
                after['tasks'].append(task); after['task_ids'].append(task['task_id'])
            elif kind == "plan" and len(parts) == 4 and parts[1] == "tasks":
                task = next((t for t in after["tasks"] if t["task_id"] == parts[2]), None)
                if task is None:
                    raise AppError("task_not_found", 404)
                field = parts[3]
                allowed = {"complete_task": {"state"}, "reschedule_task": {"scheduled_at"},
                           "replace_plan": {"scheduled_at", "estimated_hours"},
                           "edit_task": {"title", "description", "estimated_hours"},
                           "schedule_task": {"state", "scheduled_at"}}.get(req["kind"], set())
                if field not in allowed:
                    raise AppError("action_scope_field_mismatch")
                if task["locked"] or task["state"] == "completed":
                    raise AppError("completed_or_locked_task_preserved", 409)
                if task.get(field) != change["before"]:
                    raise AppError("diff_before_mismatch", 409)
                if field == "state" and change["after"] != ('scheduled' if req['kind']=='schedule_task' else 'completed'):
                    raise AppError("completion_scope_invalid")
                if field == "scheduled_at":
                    instant(change["after"])
                    if task["state"] != "scheduled" and req['kind'] != 'schedule_task':
                        raise AppError("reschedule_requires_scheduled_task", 409)
                    if task["estimated_hours"] is None:
                        raise AppError("effort_unknown_requires_clarification", 409)
                if field in ('title','description') and change['after'] is None:
                    task.pop(field,None)  # exact undo of a previously absent optional text field
                else:
                    task[field] = change["after"]
                if field == "state" and req['kind'] == 'complete_task':
                    task["activity_completion"] = True
            elif kind == 'profile' and req['kind']=='change_goal' and change['path']=='/career_context/goals':
                context = after.setdefault('career_context', {})
                if context.get('goals') != change['before']:
                    raise AppError('diff_before_mismatch',409)
                if change['after'] is None:
                    context.pop('goals',None)
                else:
                    context['goals'] = change['after']
            elif kind == "profile" and len(parts) == 4 and parts[1] == "preferences":
                entity_type, entity_id = parts[2:]
                if entity_type not in ("role", "industry", "skill", "company"):
                    raise AppError("unsupported_preference_scope")
                prior = next((p for p in after["preferences"] if
                    (p["entity_type"], p["entity_id"]) == (entity_type, entity_id)), None)
                if (prior["state"] if prior else None) != change["before"]:
                    raise AppError("diff_before_mismatch", 409)
                if prior:
                    after["preferences"].remove(prior)
                if change["after"] is not None:
                    after["preferences"].append(dict(entity_type=entity_type, entity_id=entity_id,
                        state=change["after"], authorizing_request_id="pending-authority"))
            elif kind == "profile" and len(parts) == 4 and parts[1] == "constraints" and parts[3] == "value":
                constraint = next((c for c in after["constraints"] if c["constraint_id"] == parts[2]), None)
                if constraint is None or constraint["value"] != change["before"]:
                    raise AppError("constraint_scope_mismatch", 409)
                constraint["value"] = change["after"]
            else:
                raise AppError("unsupported_action_path")
        if kind == "plan":
            from .plans import check_plan
            profile = self.store.get(owner, "profile", owner, db=db)
            feasibility = check_plan(after, profile, before)
            if req["kind"] in ('reschedule_task','replace_plan','schedule_task') and feasibility["status"] != "checked":
                raise AppError("capacity_or_effort_unknown_requires_clarification", 409)
        else:
            validate("Profile", after)
        return kind, before, after

    def _execute(self, db, owner, req, key, *, request_id=None, proposal=None):
        if request_id:
            row = db.execute("SELECT scope FROM authorities WHERE owner=? AND id=?", (owner, request_id)).fetchone()
            if row is None or row[0] != encode(req):
                raise AppError("trusted_request_authority_required", 403)
        elif proposal:
            row = db.execute("SELECT preview,status FROM proposals WHERE owner=? AND id=?",
                             (owner, proposal["proposal_id"])).fetchone()
            if row is None or row["status"] != "pending" or row["preview"] != encode(proposal):
                raise AppError("approved_preview_required", 403)
        else:
            raise AppError("authority_required", 403)
        kind, before, after = self._preview(db, owner, req)
        aid = uid()
        authority_id = request_id or proposal["proposal_id"]
        if kind == "plan" and req["kind"] == "complete_task":
            after["progress_event_ids"].append(aid)
        if kind == 'agent_settings':
            from .automation_state import save_automation_settings
            saved=save_automation_settings(_TransactionStore(self.store,db),owner,
                _automation_changes(before,req),None if before['version']=='missing' else before['version'])
        elif kind == "profile":
            for item in after["preferences"]:
                if item["authorizing_request_id"] == "pending-authority":
                    item["authorizing_request_id"] = authority_id
            saved = self.store.put(owner, kind, req["target_id"], after, req["expected_state_version"], db=db)
        else:
            saved = save_plan(self.store, owner, after, req["expected_state_version"], db=db)["plan"]
        version = saved['state_version' if kind=='plan' else 'version']
        action = dict(action_id=aid, kind=req["kind"], origin="direct_request" if request_id else proposal["origin"],
            expected_state_version=req["expected_state_version"], idempotency_key=key,
            authorizing_request_id=request_id, proposal_id=proposal["proposal_id"] if proposal else None,
            approval_state="not_required_direct" if request_id else "approved",
            approved_proposal_id=proposal["proposal_id"] if proposal else None, diff=req["diff"],
            reason=req["reason"], evidence_ids=req["evidence_ids"], execution_status="applied",
            resulting_state_version=version, failure_reason=None)
        validate("Action", action)
        result = dict(action=action, target=saved)
        audit = dict(result=result, before=before, target_id=req["target_id"], created_at=now())
        db.execute("INSERT INTO action_audit VALUES(?,?,?)", (owner, aid, encode(audit)))
        db.execute("INSERT INTO executions VALUES(?,?,?,?)", (owner, key, encode(req), encode(result)))
        from .agents import emit
        trigger = "task_completion" if req["kind"] == "complete_task" else (
            "constraints_changed" if any("/constraints/" in c["path"] for c in req["diff"]) else "preferences_changed")
        if (kind == "profile" and any(c['path'].startswith(('/preferences/','/constraints/')) for c in req['diff'])) or req["kind"] == "complete_task":
            emit(db, owner, "action:" + aid, trigger, dict(action_id=aid, resulting_version=version))
        return result

    def undo(self, owner, action_id, expected, key):
        # Undo only the exact scalar diff at the current version. Completion is
        # deliberately irreversible here, so activity evidence cannot disappear.
        with self.store.connect() as db:
            row = db.execute("SELECT body FROM action_audit WHERE owner=? AND id=?", (owner, action_id)).fetchone()
        if not row:
            raise AppError("action_not_found", 404)
        audit = json.loads(row[0])
        action = audit["result"]["action"]
        if action["kind"] == "complete_task":
            raise AppError("completion_history_preserved", 409)
        if action['kind'] in ('create_task','schedule_task','configure_automation'):
            raise AppError('use_explicit_task_controls_to_reverse_creation_or_scheduling',409)
        req = dict(kind=action["kind"], target_id=audit["target_id"], expected=expected,
                   diff=[dict(path=c["path"], before=c["after"], after=c["before"]) for c in action["diff"]],
                   reason="Explicit undo of " + action_id, evidence_ids=action["evidence_ids"])
        return self.direct(owner, req, key)
