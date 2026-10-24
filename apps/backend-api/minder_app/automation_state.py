"""Persist the existing daily schedule/result; execution remains A's one Worker."""
from datetime import datetime,timedelta,timezone
import json
import re
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from .store import AppError,now,uid
from .conversations import append_notice


def next_run(at, zone, check_time):
    local=at.astimezone(ZoneInfo(zone))
    hour,minute=map(int,check_time.split(":"))
    candidate=local.replace(hour=hour,minute=minute,second=0,microsecond=0)
    if candidate.astimezone(timezone.utc)<=at.astimezone(timezone.utc):
        candidate=(local+timedelta(days=1)).replace(hour=hour,minute=minute,second=0,microsecond=0)
    return candidate.astimezone(timezone.utc).isoformat().replace("+00:00","Z")


def save_automation_settings(store,owner,settings,expected,*,at=None):
    if (not isinstance(settings,dict) or not settings or set(settings)-{"enabled","check_time","timezone","state","scope"}):
        raise AppError("invalid_schedule_settings")
    at=at or datetime.now(timezone.utc)
    with store.transaction() as db:
        try:
            previous=store.get(owner,"agent_settings",owner,db=db)
        except AppError as error:
            if error.status!=404:
                raise
            previous=None
        if (previous["version"] if previous else None)!=expected:
            raise AppError("stale_state_version",409)
        value=dict(previous) if previous else dict(enabled=True,check_time="09:00",timezone="Asia/Kuala_Lumpur",
            state="active",scope={"plan_ids":[]},last_result=None)
        value.update(settings)
        if "state" in settings:
            if settings["state"] not in ("active","paused","cancelled"):
                raise AppError("invalid_schedule_state")
            desired=settings["state"]=="active"
            if "enabled" in settings and settings["enabled"]!=desired:
                raise AppError("schedule_state_enabled_conflict")
            value["enabled"]=desired
        elif "enabled" in settings:
            value["state"]="active" if settings["enabled"] else "paused"
        value.setdefault("timezone","Asia/Kuala_Lumpur")
        value.setdefault("scope",{"plan_ids":[]})
        value.setdefault("last_result",None)
        value.setdefault("state","active" if value["enabled"] else "paused")
        if (not isinstance(value["enabled"],bool) or not isinstance(value["check_time"],str)
                or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",value["check_time"])):
            raise AppError("invalid_local_check_time")
        try:
            ZoneInfo(value["timezone"])
        except (ZoneInfoNotFoundError,ValueError,TypeError):
            raise AppError("invalid_timezone") from None
        scope=value["scope"]
        if (not isinstance(scope,dict) or set(scope)!={"plan_ids"} or not isinstance(scope["plan_ids"],list)
                or len(scope["plan_ids"])>20 or any(not isinstance(p,str) or not p for p in scope["plan_ids"])
                or len(set(scope["plan_ids"]))!=len(scope["plan_ids"])):
            raise AppError("invalid_schedule_scope")
        for plan_id in scope["plan_ids"]:
            store.get(owner,"plan",plan_id,db=db)
        value["next_run"]=next_run(at,value["timezone"],value["check_time"]) if value["enabled"] else None
        current_date=at.astimezone(ZoneInfo(value["timezone"])).date().isoformat()
        pending=list(db.execute("SELECT id,status,payload FROM agent_events WHERE owner=? AND kind='daily_check' "
            "AND status IN ('pending','retry','processing','paused','cancelled')",(owner,)))
        for event in pending:
            if not value["enabled"]:
                status=value["state"]
            elif (previous and any(key in settings and previous.get(key)!=value.get(key)
                    for key in ("check_time","timezone","scope")) and event["status"] in ("pending","retry","processing")):
                status="cancelled"
            elif event["status"] in ("paused","cancelled"):
                status="pending" if json.loads(event["payload"]).get("local_date")==current_date else "cancelled"
            else:
                continue
            db.execute("UPDATE agent_events SET status=?,lease_until=NULL WHERE owner=? AND id=?",(status,owner,event["id"]))
        db.execute("INSERT INTO authorities VALUES(?,?,?,?)",(owner,uid(),json.dumps(dict(kind="explicit_daily_schedule",settings=settings)),now()))
        return store.put(owner,"agent_settings",owner,value,expected,db=db)


def record_automation_result(store,owner,event_id,*,db=None,at=None):
    if db is None:
        with store.transaction() as conn:
            return record_automation_result(store,owner,event_id,db=conn,at=at)
    at=at or datetime.now(timezone.utc)
    event=db.execute("SELECT status FROM agent_events WHERE owner=? AND id=? AND kind='daily_check'",(owner,event_id)).fetchone()
    if event is None:
        raise AppError("daily_run_not_found",404)
    settings=store.get(owner,"agent_settings",owner,db=db)
    previous=settings.get("last_result") or {}
    if previous.get("event_id")==event_id and previous.get("status")==event["status"]:
        return settings
    result=dict(event_id=event_id,status=event["status"],observed_at=at.astimezone(timezone.utc).isoformat().replace("+00:00","Z"))
    notice=db.execute("SELECT id FROM notices WHERE owner=? AND id=?",(owner,event_id)).fetchone()
    if notice:
        linked=append_notice(store,owner,event_id,db=db)
        result.update(notice_id=event_id,conversation_id=linked["conversation_id"],message_id=linked["message_id"])
    settings.update(last_result=result)
    settings.setdefault("timezone","Asia/Kuala_Lumpur")
    settings.setdefault("scope",{"plan_ids":[]})
    settings.setdefault("state","active" if settings["enabled"] else "paused")
    settings["next_run"]=next_run(at,settings["timezone"],settings["check_time"]) if settings["enabled"] else None
    return store.put(owner,"agent_settings",owner,settings,settings["version"],db=db)
