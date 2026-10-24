"""Synthetic identities/handler; actual canonical writes, private files and process restart."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from minder_app.api import Application
from minder_app.auth_adapter import VerifiedIdentity
from minder_app.automation_state import save_automation_settings,record_automation_result
from minder_app.conversations import Conversations
from minder_app.documents import DocumentLibrary
from minder_app.identity_store import owner_for_identity
from minder_app.plans import create_plan
from minder_app.profiles import save_profile
from minder_app.product_state import dispatch as state_dispatch
from minder_app.store import Store,AppError
from minder_ml.intelligence.policy import ROOT


def restart_read(database,owner,document_id,conversation_id):
    store=Store(database)
    service=Conversations(store)
    library=DocumentLibrary.from_environment(store,{"MINDER_DOCUMENT_STORAGE":"local-development"})
    download=library.download(owner,{"document_id":document_id})
    assert base64.b64decode(download["content_base64"])==b"Fictional Resume Education and Experience"
    profile=store.get(owner,"profile",owner)
    assert profile["career_context"]["education"]=="Reviewed fictional education"
    assert service.open(owner,{"conversation_id":conversation_id})["messages"][1]["response"]["action_status"]=="applied"
    assert store.get(owner,"agent_settings",owner)["last_result"]["status"]=="processed"
    with store.connect() as db:
        versions=[row[0] for row in db.execute("SELECT version FROM migrations ORDER BY version")]
    print(json.dumps(dict(status="passed",new_process=True,engine=store.engine,schema_version=max(versions),
        private_file_read=True,profile_read=True,visible_history_read=True,run_result_read=True)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restart-read",nargs=4)
    args=parser.parse_args()
    if args.restart_read:
        restart_read(*args.restart_read)
        return
    root=ROOT/"ml/artifacts/session-d/product"
    root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="morning-acceptance-",dir=root) as folder:
        database=Path(folder)/"runtime.sqlite3"
        store=Store(database);app=Application(store)
        anonymous=store.session()
        old=save_profile(store,anonymous["profile_id"],{"synthetic":True,"career_context":{"education":"Historical anonymous fixture"}},None)
        identities=[VerifiedIdentity("https://software-fixture.invalid",subject,"synthetic-session",2000000000)
                    for subject in ("fictional-A","fictional-B")]
        owner,other=[owner_for_identity(store,identity) for identity in identities]
        assert owner!=anonymous["profile_id"] and other!=owner
        assert store.list(owner,"profile")==[]
        profile=save_profile(store,owner,{"synthetic":True,"onboarding":{"stage":"studying"}},None)
        library=DocumentLibrary.from_environment(store,{"MINDER_DOCUMENT_STORAGE":"local-development"})
        upload=dict(filename="fictional-resume.txt",purpose="resume",content_type="text/plain",
            content_base64=base64.b64encode(b"Fictional Resume Education and Experience").decode(),idempotency_key="cv")
        doc=library.upload(owner,upload)["document"]
        assert library.upload(owner,upload)["document"]==doc
        assert library.list(other)["documents"]==[]
        reviewed=library.extract(owner,{"document_id":doc["document_id"]})
        applied=state_dispatch(app,owner,"POST","/api/product/intake-correction",dict(draft_id=reviewed["draft"]["id"],
            expected_profile_version=profile["version"],profile={"career_context":{"education":"Reviewed fictional education"}},idempotency_key="review"))
        profile=applied["profile"]
        plan=dict(plan_id="draft",profile_id=owner,selected_role_id="synthetic-role",state_version="draft",previous_version=None,
            task_ids=["fictional-task"],tasks=[dict(task_id="fictional-task",title="Fictional practice",state="proposed",
                activity_completion=False,mastery_verified=False,prerequisite_task_ids=[],locked=False,scheduled_at=None,
                estimated_hours=None,evidence_ids=[])],constraints=[],progress_event_ids=[])
        plan=create_plan(store,owner,plan,"canonical-plan")["plan"]
        service=Conversations(store)
        first=service.create(owner,{"idempotency_key":"first"})["conversation"]
        second=service.create(owner,{"idempotency_key":"second"})["conversation"]
        assert first["conversation_id"]!=second["conversation_id"]
        with ThreadPoolExecutor(max_workers=8) as pool:
            singleton=list(pool.map(lambda _:service.mindbot(owner)["conversation"]["conversation_id"],range(16)))
        assert len(set(singleton))==1
        invocations=[]
        def handler(current_owner,channel,message,history,request_id,body):
            invocations.append(request_id)
            current=store.get(current_owner,"plan",plan["plan_id"])
            result=app.actions.direct(current_owner,dict(kind="complete_task",target_id=current["plan_id"],expected=current["state_version"],
                diff=[dict(path="/tasks/fictional-task/state",before="proposed",after="completed")],reason="Explicit synthetic command",evidence_ids=[]),"turn:"+request_id)
            return dict(answer="The explicitly requested fictional task was saved.",statements=[],action_status="applied",
                actions=[result],action_ids=[result["action"]["action_id"]])
        body=dict(conversation_id=first["conversation_id"],message="Mark the fictional task completed",idempotency_key="turn",expected_profile_version=profile["version"])
        result=service.continue_turn(owner,body,handler)
        assert service.continue_turn(owner,body,handler)==result and len(invocations)==1
        assert service.open(owner,{"conversation_id":first["conversation_id"]})["messages"][1]["response"]["action_ids"]==result["response"]["action_ids"]
        try:
            service.open(other,{"conversation_id":first["conversation_id"]})
            raise AssertionError("foreign history was exposed")
        except AppError as error:
            assert error.status==404
        settings=save_automation_settings(store,owner,{"check_time":"09:00"},None,at=datetime(2026,10,24,0,0,tzinfo=timezone.utc))
        from minder_app.agents import Worker
        worker=Worker(store,app.actions)
        for _ in range(6):
            run=worker.tick(datetime(2026,10,24,1,0,tzinfo=timezone.utc),owner=owner)
            if run.get("event_id","").startswith("daily:2026-10-24"):
                break
        assert run.get("event_id","").startswith("daily:2026-10-24") and run["status"]=="processed"
        record_automation_result(store,owner,run["event_id"],at=datetime(2026,10,24,1,0,tzinfo=timezone.utc))
        assert service.mindbot(owner)["conversation"]["conversation_id"]==singleton[0]
        env={key:os.environ[key] for key in ("PATH","PYTHONPATH","LANG") if key in os.environ}
        env["PYTHONDONTWRITEBYTECODE"]="1"
        child=subprocess.run([sys.executable,"-B",str(Path(__file__).resolve()),"--restart-read",str(database),owner,doc["document_id"],first["conversation_id"]],
            capture_output=True,text=True,timeout=20,env=env)
        assert child.returncode==0, "fresh process read failed (private diagnostics withheld)"
        restart=json.loads(child.stdout)
        assert restart["new_process"] and restart["schema_version"]==7
        store.backup(Path(folder)/"backups/private.sqlite3")
        library.delete(owner,dict(document_id=doc["document_id"],expected_version=reviewed["document"]["version"],idempotency_key="delete-cv"))
        assert library.list(owner)["documents"]==[] and list((Path(folder)/"uploads/documents").iterdir())==[]
        assert store.get(owner,"profile",owner)==profile
        assert store.get(anonymous["profile_id"],"profile",anonymous["profile_id"])==old
        with store.connect() as db:
            assert db.execute("SELECT count(*) FROM drafts WHERE owner=?",(owner,)).fetchone()[0]==0
    print(json.dumps(dict(status="passed",schema_version=7,engine="sqlite",identity="software VerifiedIdentity fixtures, not live login",
        model="explicit software handler, no provider invocation",storage="actual configured local-development private files",
        hosted_durability="unverified_access_pending",checks=["anonymous_not_claimed","two_owner_isolation","CV_review_apply",
        "multiple_Minder","concurrent_single_Mindbot","actual_action_reference","exact_retry_no_action_replay",
        "real_existing_Worker_daily_notice","same_Mindbot_run_result","fresh_process_restart","private_DB_backup",
        "CV_byte_and_draft_deletion","accepted_profile_retained"])))


if __name__=="__main__":
    main()
