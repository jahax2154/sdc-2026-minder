"""Version visible generated drafts; accept once into the existing canonical plan graph."""
import copy
import hashlib
import json
from jsonschema import Draft202012Validator
from .generation_schemas import VALIDATOR, POLICY_ID
from .plans import create_plan
from .store import AppError, now

ID = {"type":"string","minLength":1,"maxLength":200}
ACCEPT_SCHEMA = dict(type="object",additionalProperties=False,
    required=["draft_id","role_id","expected_profile_version","expected_generation_version","idempotency_key"],
    properties=dict(draft_id=ID,role_id=ID,expected_profile_version=ID,expected_generation_version=ID,idempotency_key=ID))
OPERATIONS = (("GET","/api/product/generations"),("POST","/api/product/generation"),("POST","/api/product/generation-accept"))


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def record_generation(store, owner, generation):
    """Internal server hook after A validates a real generated response; no tools."""
    required={"policy_version","draft_id","status","model","profile_version","advice","claim_scope"}
    if not isinstance(generation,dict) or not required.issubset(generation) or set(generation)-required:
        raise AppError("invalid_generation_record")
    if (generation["policy_version"]!=POLICY_ID or not isinstance(generation["draft_id"],str)
            or not 1<=len(generation["draft_id"])<=200 or not isinstance(generation["model"],str)
            or not 1<=len(generation["model"])<=200 or len(encoded(generation).encode())>65536):
        raise AppError("invalid_generation_record")
    VALIDATOR.validate(generation["advice"])
    if (generation["status"]!="unsaved_draft" or not isinstance(generation["claim_scope"],str)
            or len(generation["claim_scope"])>2000 or (generation["profile_version"] is not None
                and (not isinstance(generation["profile_version"],str) or not 1<=len(generation["profile_version"])<=200))):
        raise AppError("invalid_generation_record")
    from .product_migrations import migrate
    migrate(store)
    with store.transaction() as db:
        if generation["profile_version"] is not None and not db.execute(
                "SELECT 1 FROM history WHERE owner=? AND kind='profile' AND id=? AND version=?",
                (owner,owner,generation["profile_version"])).fetchone():
            raise AppError("generation_profile_reference_not_owned",409)
        try:
            previous=store.get(owner,"generation",generation["draft_id"],db=db)
        except AppError as error:
            if error.status!=404:
                raise
            previous=None
        if previous:
            if previous["generation"]!=generation:
                raise AppError("generation_id_scope_conflict",409)
            return previous
        return store.put(owner,"generation",generation["draft_id"],dict(draft_id=generation["draft_id"],
            generation=copy.deepcopy(generation),status="generated",created_at=now(),accepted_plan_id=None,
            accepted_state_version=None),None,db=db)


def accept_generation(app, owner, body):
    Draft202012Validator(ACCEPT_SCHEMA).validate(body)
    store=app.store
    scope=hashlib.sha256(encoded(dict(operation="accept_generation",body=body)).encode()).hexdigest()
    def retry(db):
        previous=db.execute("SELECT scope,result FROM product_requests WHERE owner=? AND key=?",(owner,body["idempotency_key"])).fetchone()
        if previous:
            if previous["scope"]!=scope:
                raise AppError("idempotency_scope_conflict",409)
            return json.loads(previous["result"])
    with store.connect() as db:
        db.execute("BEGIN")
        result=retry(db)
        if result is not None:
            return result
        record=store.get(owner,"generation",body["draft_id"],db=db)
    if record["status"]!="generated":
        raise AppError("generation_already_accepted",409)
    if record["version"]!=body["expected_generation_version"]:
        raise AppError("stale_state_version",409)
    if record["generation"]["profile_version"]!=body["expected_profile_version"]:
        raise AppError("generation_profile_stale",409)
    materialize=getattr(app,"generation_materializer",None)
    if not callable(materialize):
        raise AppError("generation_materializer_unavailable",503)
    # Pure A validation/materialization callback, deliberately outside transactions.
    plan=materialize(owner,copy.deepcopy(record["generation"]),body["role_id"])
    if (plan.get("selected_role_id")!=body["role_id"] or any(t["state"]!="proposed"
            or t["activity_completion"] or t["mastery_verified"] or t["locked"]
            or t["scheduled_at"] is not None for t in plan.get("tasks",[]))):
        raise AppError("generation_cannot_imply_completed_or_scheduled_tasks")
    with store.transaction() as db:
        result=retry(db)
        if result is not None:
            return result
        current=store.get(owner,"generation",body["draft_id"],db=db)
        profile=store.get(owner,"profile",owner,db=db)
        if current["version"]!=body["expected_generation_version"] or current["status"]!="generated":
            raise AppError("stale_state_version",409)
        if profile["version"]!=body["expected_profile_version"]:
            raise AppError("generation_profile_stale",409)
        draft=current["generation"]
        provenance=dict(generation_id=body["draft_id"],generation_version=current["version"],
            model=draft["model"],policy_version=draft["policy_version"],profile_version=draft["profile_version"],
            fact_ids=draft["advice"]["fact_ids"],assumptions=draft["advice"]["assumptions"])
        saved=create_plan(store,owner,plan,"generation:"+hashlib.sha256(body["idempotency_key"].encode()).hexdigest(),provenance,db=db)
        current.update(status="accepted",accepted_plan_id=saved["plan"]["plan_id"],
                       accepted_state_version=saved["plan"]["state_version"],accepted_at=now())
        current=store.put(owner,"generation",body["draft_id"],current,current["version"],db=db)
        result=dict(generation=current,plan=saved["plan"],feasibility=saved["feasibility"],
                    activated=False,requires_explicit_direction_selection=True)
        db.execute("INSERT INTO product_requests VALUES(?,?,?,?)",(owner,body["idempotency_key"],scope,encoded(result)))
        return result


def dispatch(app,owner,method,path,body):
    if (method,path) not in OPERATIONS:
        raise AppError("product_capability_unavailable",404)
    if path.endswith("/generations"):
        Draft202012Validator(dict(type="object",additionalProperties=False)).validate(body)
        return dict(generations=app.store.list(owner,"generation"))
    if path.endswith("/generation-accept"):
        return accept_generation(app,owner,body)
    Draft202012Validator(dict(type="object",additionalProperties=False,required=["draft_id"],properties=dict(draft_id=ID))).validate(body)
    return dict(generation=app.store.get(owner,"generation",body["draft_id"]))
