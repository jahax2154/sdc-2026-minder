from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from support import AppCase,fixture
from minder_app.generation_state import record_generation,accept_generation
from minder_app.generation_schemas import POLICY_ID
from minder_app.store import AppError,Store


class GenerationStateTests(AppCase):
    def setUp(self):
        super().setUp()
        self.profile=self.save();self.owner=self.profile["profile_id"]
        self.generation=dict(policy_version=POLICY_ID,draft_id="fictional-generated",status="unsaved_draft",
            model="software-fixture-no-real-provider",profile_version=self.profile["version"],
            claim_scope="Fictional proposed guidance, not competence",advice=dict(kind="roadmap",
                answer="A fictional generated practice outline for persistence testing.",assumptions=[],questions=[],
                stages=[dict(title="Practice",outcome="Document a fictional exercise",tasks=[dict(title="Practice",description="Fictional activity",estimated_hours=None)])],
                fact_ids=[],operation=dict(kind="none",task_id=None,scheduled_at=None,instruction_quote=None)))
        self.app.generation_materializer=self.materialize

    def materialize(self,owner,generation,role_id):
        plan=fixture("plan_progress")
        plan.update(profile_id=owner,selected_role_id=role_id)
        for task in plan["tasks"]:
            task.update(state="proposed",scheduled_at=None)
        return plan

    def body(self,record,key="accept"):
        return dict(draft_id=record["draft_id"],role_id="synthetic-role",expected_profile_version=self.profile["version"],
            expected_generation_version=record["version"],idempotency_key=key)

    def test_generated_and_accepted_versions_single_canonical_graph_retry_restart(self):
        record=record_generation(self.store,self.owner,self.generation)
        self.assertEqual(record_generation(self.store,self.owner,self.generation),record)
        self.assertEqual(self.store.list(self.owner,"plan"),[])
        body=self.body(record)
        with ThreadPoolExecutor(max_workers=4) as pool:
            accepted=list(pool.map(lambda _:accept_generation(self.app,self.owner,body),range(8)))
        self.assertTrue(all(a==accepted[0] for a in accepted))
        self.assertEqual(len(self.store.list(self.owner,"plan")),1)
        self.assertFalse(accepted[0]["activated"])
        self.assertEqual(self.store.list(self.owner,"direction"),[])
        stored=Store(self.store.path).get(self.owner,"generation",record["draft_id"])
        self.assertEqual(stored["status"],"accepted")
        self.assertEqual(stored["accepted_plan_id"],accepted[0]["plan"]["plan_id"])
        self.assertFalse(accepted[0]["plan"]["tasks"][0]["mastery_verified"])
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM history WHERE owner=? AND kind='generation'",(self.owner,)).fetchone()[0],2)
        self.assertEqual(accept_generation(self.app,self.owner,body),accepted[0])
        with self.assertRaises(AppError):
            accept_generation(self.app,self.owner,dict(body,role_id="different-role"))

    def test_stale_profile_foreign_draft_and_immutable_generated_content(self):
        record=record_generation(self.store,self.owner,self.generation)
        with self.assertRaises(AppError):
            record_generation(self.store,self.owner,dict(self.generation,claim_scope="Changed same draft identity"))
        other=self.store.session()["profile_id"]
        with self.assertRaises(AppError):
            accept_generation(self.app,other,self.body(record))
        with self.assertRaises(AppError):
            record_generation(self.store,other,self.generation)
        self.app.dispatch("PUT","/api/profile",dict(profile={"career_context":{"goals":"Changed fictional direction"}},expected_version=self.profile["version"]),self.token)
        with self.assertRaises(AppError) as error:
            accept_generation(self.app,self.owner,self.body(record))
        self.assertEqual(error.exception.code,"generation_profile_stale")
        self.assertEqual(self.store.list(self.owner,"plan"),[])

    def test_materializer_failure_or_completed_task_never_partially_accepts(self):
        record=record_generation(self.store,self.owner,self.generation)
        def bad(owner,generation,role_id):
            plan=self.materialize(owner,generation,role_id)
            plan["tasks"][0].update(state="completed",activity_completion=True)
            return plan
        self.app.generation_materializer=bad
        with self.assertRaises(AppError):
            accept_generation(self.app,self.owner,self.body(record))
        self.assertEqual(self.store.get(self.owner,"generation",record["draft_id"])["status"],"generated")
        self.assertEqual(self.store.list(self.owner,"plan"),[])
