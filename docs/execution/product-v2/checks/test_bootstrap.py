"""Actual source/WSGI first slice and migration/auth/namespace compatibility."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from referencing import Registry, Resource
from jsonschema import Draft202012Validator
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.integration_cli import application, wsgi_request
from minder_ml.intelligence.product_runtime import build, web_app
from minder_ml.intelligence.groq_adapter import GroqAdapter
from minder_ml.intelligence.service_contracts import validate

class BootstrapTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'ml/artifacts/session-a/p0-bootstrap/tests';base.mkdir(parents=True,exist_ok=True)
        self.folder=tempfile.TemporaryDirectory(dir=base)
        self.app,_=application(Path(self.folder.name)/'runtime.sqlite3',role_ids=['onet:15-1252.00'],
            provider=GroqAdapter(key='',model='qwen/qwen3.8-27b'))
        self.token=wsgi_request(self.app,'POST','/api/session',{})[1]['token']
    def tearDown(self):self.folder.cleanup()
    def test_auth_unavailable_and_actual_capability_example(self):
        path='/api/product/capabilities'
        self.assertEqual(wsgi_request(self.app,'GET',path)[0],401)
        code,result=wsgi_request(self.app,'GET',path,token=self.token)
        self.assertEqual(code,200);self.assertTrue(result['operations'])
        self.assertTrue(all(x['status'] in ('implemented','unavailable') for x in result['operations']))
        self.assertEqual(wsgi_request(self.app,'GET','/api/product/unregistered',token=self.token)[0],404)
        direction=next(x for x in result['operations'] if x['method']=='PUT' and x['path']=='/api/product/direction')
        self.assertEqual(wsgi_request(self.app,'PUT','/api/product/direction',
            {'role_id':'onet:15-1252.00'},self.token)[0],422 if direction['status']=='implemented' else 404)
    def test_profile_metadata_is_optional_and_not_skill_evidence(self):
        from minder_ml.intelligence.integration_cli import provisional_demo_profile
        body=provisional_demo_profile('incomplete',(2,))
        body['career_context']={'display_name':'Fictional Graduate','education':'Fictional degree','experience':'No prior job','goals':'Explore options'}
        code,saved=wsgi_request(self.app,'PUT','/api/profile',dict(profile=body,expected_version=None),self.token)
        self.assertEqual(code,200);self.assertEqual(saved['career_context'],body['career_context'])
        result=self.app.services.personal.assess(saved,self.app.services.roles)
        self.assertEqual(result['public']['coverage']['assessed'],0)
        self.assertTrue(result['public']['targeted_questions'])
        other=wsgi_request(self.app,'POST','/api/session',{})[1]['token']
        self.assertEqual(wsgi_request(self.app,'GET','/api/profile',token=other)[0],404)
    def test_no_cross_namespace_or_unknown_namespace_and_static_secret(self):
        provider=GroqAdapter(key='',model='qwen/qwen3.8-27b')
        with self.assertRaises(ValueError):application(ROOT/'ml/artifacts/session-d/x.sqlite3',provider=provider)
        with self.assertRaises(ValueError):application(ROOT/'ml/artifacts/session-a/x.sqlite3',namespace='session-z',provider=provider)
        status=[]
        answer=web_app(self.app)({'PATH_INFO':'/../../.env.groq.local','REQUEST_METHOD':'GET'},lambda code,headers:status.append(code))
        self.assertEqual(status[0],'404 Not Found');self.assertNotIn(b'GROQ',b''.join(answer))
    def test_strict_first_slice_schema_and_existing_task_compatibility(self):
        shared=json.loads((ROOT/'contracts/parallel-services.v1.schema.json').read_text())
        contract=json.loads((ROOT/'docs/execution/product-v2/contracts.schema.json').read_text())
        Draft202012Validator.check_schema(contract)
        registry=Registry().with_resource(shared['$id'],Resource.from_contents(shared))
        for name,payload in [('DirectionWrite',dict(role_id='onet:15-1252.00',expected_version=None,idempotency_key='fictional-select')),
                             ('ResourceStateWrite',dict(resource_id='source-term:python',saved=True,dismissed=False,expected_version=None,idempotency_key='fictional-save'))]:
            Draft202012Validator({'$ref':'#/$defs/'+name,'$defs':contract['$defs']},registry=registry).validate(payload)
        task=dict(task_id='fictional-task',state='proposed',activity_completion=False,mastery_verified=False,
            prerequisite_task_ids=[],locked=False,scheduled_at=None,estimated_hours=None,evidence_ids=[],title='User activity',resource_id=None,skill_ids=[])
        validate('Task',task)
        payload=dict(plan_id='fictional-plan',expected_state_version='v1',idempotency_key='fictional-create',task=task)
        Draft202012Validator({'$ref':'#/$defs/TaskCreate','$defs':contract['$defs']},registry=registry).validate(payload)

if __name__=='__main__':unittest.main()
