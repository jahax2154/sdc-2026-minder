"""Real source/WSGI trace boundary; synthetic users, no provider or network mocks."""
import json
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from minder_ml.intelligence.integration_cli import application,provisional_demo_profile,wsgi_request
from minder_ml.intelligence.policy import ROOT


class EvidenceApiTests(unittest.TestCase):
    def setUp(self):
        root=ROOT/'ml/artifacts/session-a/evidence-api-tests';root.mkdir(parents=True,exist_ok=True)
        self.folder=tempfile.TemporaryDirectory(dir=root)
        self.app,_=application(Path(self.folder.name)/'runtime.sqlite3',role_ids=[
            'onet:15-1252.00','onet:13-2011.00','onet:11-1011.00','onet:15-2051.00','onet:17-2112.00'])
        self.token=self.request('POST','/api/session')['token']
        self.profile=self.request('PUT','/api/profile',dict(profile=provisional_demo_profile(),expected_version=None))

    def tearDown(self):self.folder.cleanup()

    def request(self,method,path,body=None,token=None,expected=200):
        code,value=wsgi_request(self.app,method,path,body,self.token if token is None and hasattr(self,'token') else token or '')
        self.assertEqual(code,expected)
        return value

    def test_source_counts_scope_and_versioned_trace_are_public_without_internal_scores(self):
        context=self.request('GET','/api/career-context')
        option=next(o for o in context['recommendation']['options'] if o['role_id']=='onet:15-1252.00')
        result=self.request('POST','/api/role-evidence',dict(role_id=option['role_id'],trace_id=option['trace_id'],
            expected_profile_version=self.profile['version']))
        kinds={r['measurement_type']:r for r in result['records']}
        self.assertEqual(kinds['employer_observation']['value'],5)
        self.assertEqual(kinds['published_offering_activity']['value'],19899)
        self.assertEqual(kinds['occupation_shortage']['value'],1)
        self.assertIsNone(kinds['occupation_shortage']['published_at'])
        self.assertFalse(kinds['occupation_shortage']['source_scope']['applies_to_all_children'])
        self.assertEqual(result['trace']['trace_id'],option['trace_id'])
        serialized=json.dumps(result)
        for forbidden in ('current_index','current_points','final_internal_score','Fictional study-project'):
            self.assertNotIn(forbidden,serialized)
        self.assertEqual(context['recommendation']['coverage']['current_comparable_ranked'],5)

    def test_auth_stale_profile_cross_user_and_unknown_role_are_rejected(self):
        self.request('POST','/api/role-evidence',dict(role_id='onet:15-1252.00'),token='invalid',expected=401)
        self.request('POST','/api/role-evidence',dict(role_id='not-in-catalogue'),expected=404)
        context=self.request('GET','/api/career-context');option=context['recommendation']['options'][0]
        body=dict(role_id=option['role_id'],trace_id=option['trace_id'],expected_profile_version='stale')
        self.request('POST','/api/role-evidence',body,expected=409)
        second=self.request('POST','/api/session')['token']
        other=self.request('PUT','/api/profile',dict(profile=provisional_demo_profile(),expected_version=None),token=second)
        body['expected_profile_version']=other['version']
        self.request('POST','/api/role-evidence',body,token=second,expected=409)

    def test_all_native_context_is_explorable_without_inventing_canonical_links(self):
        before=self.request('GET','/api/profile')
        catalogue=self.request('GET','/api/source-market-catalogue')
        self.assertEqual(len(catalogue['records']),96)
        result=self.request('POST','/api/source-market-context',dict(occupation_system='MASCO',occupation_version='2020',occupation_code='2512-01'))
        self.assertEqual(result['status'],'available')
        self.assertEqual(result['records'][0]['query_scope']['relationship'],'explicitly_enumerated_six_digit_member')
        self.assertFalse(result['records'][0]['coverage']['applies_to_all_six_digit_children'])
        unknown=self.request('POST','/api/source-market-context',dict(occupation_system='MASCO',occupation_version='2020',occupation_code='2512-99'))
        self.assertEqual(unknown['status'],'unknown');self.assertEqual(unknown['records'],[])
        self.request('POST','/api/source-market-context',dict(occupation_system='O*NET',occupation_version='2019',occupation_code='15-1252.00'),expected=422)
        self.assertEqual(before,self.request('GET','/api/profile'))

    def test_actual_A_source_registry_matches_C_verified_inspected_derivation(self):
        from minder_app.grounding import build_bundle,resolve_claim
        services=self.app.services
        context=services.career_context(self.profile,expected_profile_version=self.profile['version'],
            selected_role_ids=['onet:15-1252.00'],selected_skill_ids=['source-term:python'])
        bundle=build_bundle(context,services,[],self.profile['version'])
        observed=[resolve_claim(c,bundle) for c in bundle['claims'] if c.get('kind')=='current']
        self.assertEqual(len(observed),2)
        self.assertTrue(all(c['status']=='available' and c['sources'] for c in observed))
        registered=next(s for s in services.sources if s['source_id']=='bosch-smartrecruiters-my')
        self.assertEqual(registered['sha256'],services.market.version)
        bad=copy.deepcopy(context)
        next(s for s in bad['sources'] if s['source_id']=='bosch-smartrecruiters-my')['sha256']=hashlib.sha256(
            (ROOT/'ml/data/market/snapshot.v1.json').read_bytes()).hexdigest()
        rejected=build_bundle(bad,services,[],self.profile['version'])
        self.assertFalse(any(c.get('kind')=='current' and c.get('status')=='available' for c in rejected['claims']))

if __name__=='__main__':unittest.main()
