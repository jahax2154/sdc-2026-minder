from datetime import datetime,timezone
import json
from support import AppCase
from minder_app.automation_state import save_automation_settings,record_automation_result,next_run
from minder_app.conversations import Conversations
from minder_app.store import AppError,Store


class AutomationStateTests(AppCase):
    def setUp(self):
        super().setUp()
        self.plan=self.make_plan()["plan"];self.owner=self.profile["profile_id"]
        self.at=datetime(2026,10,24,0,0,tzinfo=timezone.utc)
        self.service=Conversations(self.store)

    def test_canonical_schedule_scope_timezone_version_and_pause_cancel(self):
        settings=save_automation_settings(self.store,self.owner,dict(check_time="09:00",scope={"plan_ids":[self.plan["plan_id"]]}),None,at=self.at)
        self.assertEqual(settings["timezone"],"Asia/Kuala_Lumpur")
        self.assertEqual(settings["next_run"],"2026-10-24T01:00:00Z")
        with self.store.transaction() as db:
            db.execute("INSERT INTO agent_events VALUES(?,?,?,?,?,?,?,?)",(self.owner,"daily:2026-10-24","daily_check",json.dumps({"local_date":"2026-10-24"}),"processing",1,"future",None))
        paused=save_automation_settings(self.store,self.owner,{"state":"paused"},settings["version"],at=self.at)
        self.assertFalse(paused["enabled"]);self.assertIsNone(paused["next_run"])
        with self.store.connect() as db:
            event=db.execute("SELECT status,lease_until FROM agent_events").fetchone()
            self.assertEqual(tuple(event),("paused",None))
        resumed=save_automation_settings(self.store,self.owner,{"state":"active"},paused["version"],at=self.at)
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT status FROM agent_events").fetchone()[0],"pending")
        cancelled=save_automation_settings(self.store,self.owner,{"state":"cancelled"},resumed["version"],at=self.at)
        self.assertEqual(cancelled["state"],"cancelled")
        self.assertEqual(Store(self.store.path).get(self.owner,"agent_settings",self.owner),cancelled)
        with self.assertRaises(AppError):
            save_automation_settings(self.store,self.owner,{"enabled":True},settings["version"],at=self.at)
        with self.assertRaises(AppError):
            save_automation_settings(self.store,self.owner,{"scope":{"plan_ids":["foreign-plan"]}},cancelled["version"],at=self.at)

    def test_real_persisted_run_reference_and_single_history_result(self):
        settings=save_automation_settings(self.store,self.owner,{"check_time":"09:00"},None,at=self.at)
        conversation=self.service.mindbot(self.owner)["conversation"]["conversation_id"]
        with self.store.transaction() as db:
            db.execute("INSERT INTO agent_events VALUES(?,?,?,?,?,?,?,?)",(self.owner,"daily:2026-10-24","daily_check","{}","processed",1,None,"{}"))
            db.execute("INSERT INTO notices VALUES(?,?,?)",(self.owner,"daily:2026-10-24",json.dumps({"summary":"Actual persisted fictional activity result"})))
            saved=record_automation_result(self.store,self.owner,"daily:2026-10-24",db=db,at=self.at)
        repeated=record_automation_result(self.store,self.owner,"daily:2026-10-24",at=self.at)
        self.assertEqual(saved,repeated)
        self.assertEqual(saved["last_result"]["status"],"processed")
        self.assertEqual(saved["last_result"]["conversation_id"],conversation)
        self.assertEqual(len(self.service.mindbot(self.owner)["messages"]),1)
        with self.assertRaises(AppError):
            record_automation_result(self.store,self.store.session()["profile_id"],"daily:2026-10-24",at=self.at)

    def test_invalid_or_unauthorized_schedule_and_timezone_date_boundary(self):
        self.assertEqual(next_run(datetime(2026,10,24,23,0,tzinfo=timezone.utc),"Asia/Kuala_Lumpur","06:00"),"2026-10-25T22:00:00Z")
        for settings in ({"check_time":"25:00"},{"timezone":"Not/AZone"},{"state":"active","enabled":False},
                         {"scope":{"plan_ids":[],"autonomous_edits":True}}):
            with self.assertRaises(AppError):
                save_automation_settings(self.store,self.owner,settings,None,at=self.at)
        self.assertEqual(self.store.list(self.owner,"agent_settings"),[])
