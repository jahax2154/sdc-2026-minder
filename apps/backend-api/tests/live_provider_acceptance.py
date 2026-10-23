"""Post-confirmation real app/provider/wall-clock worker acceptance, booleans only.

Run only after user confirmation, access verification and C server restart.
Uses real A/B context and one synthetic user in C's reserved dev database.
"""
import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request, urlopen
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
BASE = "http://127.0.0.1:9103/api/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration-confirmed", action="store_true", required=True)
    parser.parse_args()
    checks = {name: False for name in ("app_chat_request_success", "native_tool_request_success",
        "direct_change_request_success", "proactive_preview_no_mutation", "rejection_request_success",
        "approval_request_success", "persistence_check_success", "actual_scheduled_event_success",
        "scheduled_native_tool_request_success", "company_evidence_request_success", "learning_source_request_success")}
    worker = None
    token = ""
    def api(route, body=None, method=None):
        raw = json.dumps(body).encode() if body is not None else None
        request = Request(BASE + route, data=raw, method=method or ("POST" if body is not None else "GET"),
            headers={"Content-Type":"application/json", "Authorization":"Bearer " + token})
        with urlopen(request, timeout=45) as response:
            return json.loads(response.read())
    try:
        session = api("session", {})
        token, owner = session["token"], session["profile_id"]
        profile = dict(profile_id="new", profile_group_id="new", version="new", synthetic=True,
            evidence=[], preferences=[], current_fields=[], constraints=[dict(constraint_id="hours", scope="weekly_hours",
            hard=True,value=5,unit="hours_per_week",evidence_id="synthetic-user-availability")], timezone="Asia/Kuala_Lumpur")
        profile = api("profile",dict(profile=profile,expected_version=None),"PUT")
        reply = api("chat",dict(message="Explain the saved role evidence and distinguish current observations from next quarter.",
            expected_profile_version=profile["version"],selected_role_ids=["onet:15-1252.00"],selected_skill_ids=["source-term:python"]))
        checks["app_chat_request_success"] = reply["provider"]["status"] == "available"
        checks["native_tool_request_success"] = reply["provider"].get("tool_call",{}).get("arguments_validated") is True
        assert checks["app_chat_request_success"] and checks["native_tool_request_success"]
        assert "internal_index" not in json.dumps(reply)
        assert all(f["status"] == "unavailable" for f in reply["statements"] if f.get("kind") == "forecast")
        def create(task):
            p = dict(plan_id="new",profile_id=owner,selected_role_id="onet:15-1252.00",state_version="new",
                previous_version=None,task_ids=[task["task_id"]],tasks=[task],progress_event_ids=[],constraints=[])
            return api("plans",dict(plan=p,idempotency_key=str(uuid.uuid4())))["plan"]
        task = dict(task_id="explicit-activity",state="proposed",activity_completion=False,mastery_verified=False,
            prerequisite_task_ids=[],locked=False,scheduled_at=None,estimated_hours=None,evidence_ids=[])
        first = create(task)
        command = dict(request=dict(kind="complete_task",target_id=first["plan_id"],expected=first["state_version"],
            diff=[dict(path="/tasks/explicit-activity/state",before="proposed",after="completed")],
            reason="Explicit synthetic live-provider acceptance completion"),idempotency_key=str(uuid.uuid4()))
        result = api("direct-action",command)
        assert result == api("direct-action",command)
        checks["direct_change_request_success"] = (result["action"]["approval_state"] == "not_required_direct" and
            result["target"]["tasks"][0]["activity_completion"] and not result["target"]["tasks"][0]["mastery_verified"])
        # Drain only this completion before introducing overdue schedule work.
        subprocess.run([sys.executable,"-m","minder_app.worker","--once","--owner",owner],cwd=ROOT,
            check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        local = datetime.now(ZoneInfo(profile["timezone"]))
        old = (local-timedelta(days=2)).replace(hour=9,minute=0,second=0,microsecond=0).isoformat()
        task = dict(task_id="scheduled-review",state="scheduled",activity_completion=False,mastery_verified=False,
            prerequisite_task_ids=[],locked=False,scheduled_at=old,estimated_hours=1,evidence_ids=[])
        plan = create(task)
        target_time = (local-timedelta(days=1)).replace(hour=9,minute=0,second=0,microsecond=0).isoformat()
        req = dict(kind="reschedule_task",target_id=plan["plan_id"],expected=plan["state_version"],
            diff=[dict(path="/tasks/scheduled-review/scheduled_at",before=old,after=target_time)],
            reason="Review a proactive scoped schedule proposal")
        pending = api("proposals",dict(request=req))
        read_plan = lambda: next(p for p in api("plans")["plans"] if p["plan_id"] == plan["plan_id"])
        checks["proactive_preview_no_mutation"] = read_plan() == plan
        decision = dict(proposal_id=pending["preview"]["proposal_id"],decision="reject",
            preview_hash=pending["preview_hash"],expected_state_version=plan["state_version"])
        api("proposal-decision",decision)
        checks["rejection_request_success"] = read_plan() == plan
        pending = api("proposals",dict(request=req))
        decision.update(proposal_id=pending["preview"]["proposal_id"],decision="approve",preview_hash=pending["preview_hash"])
        approved = api("proposal-decision",decision)
        checks["approval_request_success"] = approved == api("proposal-decision",decision)
        from minder_app.store import Store
        saved = Store(os.environ["MINDER_DB_PATH"])
        checks["persistence_check_success"] = saved.get(owner,"plan",plan["plan_id"]) == approved["target"]
        before_scheduled = read_plan()
        # Upcoming real local minute. No injected clock/tick/event is used.
        due = (datetime.now(ZoneInfo(profile["timezone"])) + timedelta(minutes=1)).replace(second=0,microsecond=0)
        api("agent-settings",dict(settings=dict(enabled=True,check_time=due.strftime("%H:%M")),expected_version=None),"PUT")
        if due.date() != datetime.now(ZoneInfo(profile["timezone"])).date():
            while datetime.now(ZoneInfo(profile["timezone"])).date() < due.date():
                time.sleep(.5)
        worker = subprocess.Popen([sys.executable,"-m","minder_app.worker","--owner",owner,"--poll-seconds","1"],
            cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 90
        event_id = "daily:" + due.date().isoformat()
        while time.monotonic() < deadline:
            state = api("agents")
            event = next((e for e in state["events"] if e["id"] == event_id and e["status"] == "processed"),None)
            notice = next((n for n in state["notices"] if n["event_id"] == event_id),None)
            if event and notice:
                checks["actual_scheduled_event_success"] = datetime.now(ZoneInfo(profile["timezone"])) >= due
                checks["scheduled_native_tool_request_success"] = notice["provider_status"] == "available_candidate_selection"
                assert read_plan() == before_scheduled, "scheduled analysis must not mutate the plan"
                break
            time.sleep(.5)
        company = api("company-explorer",dict(employer_id="bosch",role_id="onet:15-1252.00"))
        checks["company_evidence_request_success"] = (company["result"]["status"] == "found" and
            bool(company["result"]["unknown_requirements"]) and not company["main_recommendations_changed"])
        resources = api("learning-resources",dict(topic_ids=["source-term:python"]))["resources"]
        checks["learning_source_request_success"] = bool(resources) and resources[0]["estimated_hours"] is None
    except Exception:
        pass  # no response text, secrets, headers, tokens or traceback locals
    finally:
        if worker is not None:
            worker.terminate()
            try:
                worker.wait(timeout=5)
            except subprocess.TimeoutExpired:
                worker.kill()
                worker.wait(timeout=5)
    target = ROOT / "ml/artifacts/session-c/live-provider-acceptance.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(checks,sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
