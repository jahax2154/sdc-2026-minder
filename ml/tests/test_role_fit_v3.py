"""Sourced roles, fictional anchored evidence; software invariants, not career validity."""
import copy
import json
import unittest
from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.personal_cli import synthetic_profile
from minder_ml.intelligence.personal_service import update_preference
from minder_ml.intelligence.role_fit import RoleFitService, reference, POLICY_ID, LEGACY_MARKET_POLICY
from minder_ml.intelligence.integration_cli import role_aliases
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.service_contracts import validate, public_recommendation
from minder_ml.intelligence.policy import ROOT
STAMP = '2026-10-24T00:00:00Z'


def anchored_profile(audience='fresh_graduate', levels=(2,4,4)):
    p = synthetic_profile(audience)
    source = copy.deepcopy(p['evidence'][0]['provenance']);source['evidence_type']='synthetic-fixture'
    p.update(evidence=[], preferences=[], constraints=[])
    for i,(sid,level) in enumerate(zip(sorted(reference()['skills']),levels)):
        p['evidence'].append(dict(evidence_id='fictional-anchored-'+str(i),subject_id=sid,value=level,
            unit='onet:LV',state='known',provenance=source,method_id='minder-anchored-evidence-v1',
            assessment=dict(kind='self_report',statement='Fictional source activity demonstrated in a study project.',
                            rubric_version='onet31-essential-anchors-v1')))
    return validate('Profile',p)


def optional(p,subject,kind,value):
    method={'transferable_background':'minder-transferable-background-v1',
            'work_style_preference':'minder-work-style-preference-v1'}[kind]
    e=copy.deepcopy(p['evidence'][0]);e.update(evidence_id=subject,subject_id=subject,value=value,
        unit='fraction_0_1',method_id=method,assessment=dict(kind=kind,
        statement='Fictional explicit description supporting this optional rubric response.',rubric_version=method))
    p['evidence'].append(e)


def feedback(p,rid,state,kind='role'):
    return update_preference(p,entity_type=kind,entity_id=rid,state=state,
        authorizing_request_id='fictional-explicit-request',expected_profile_version=p['version'])


class RoleFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=OccupationalCatalogue()
        cls.roles=[cls.cat.role(r) for r in ('onet:15-1252.00','onet:15-2051.00','onet:11-1011.00')]
        cls.market=MarketEvidenceService(aliases={'role':role_aliases(cls.cat)})

    def result(self,p=None,market=None,**kwargs):
        kwargs.setdefault('market_period_policy_key',LEGACY_MARKET_POLICY)  # frozen v1 combination regressions
        return RoleFitService(market,as_of=STAMP).assess(p or anchored_profile(),self.roles,**kwargs)

    def test_minimum_fresh_graduate_optional_missing(self):
        r=self.result();self.assertEqual(r['public']['coverage']['assessed'],3)
        self.assertFalse(r['public']['overall_ranking_complete'])
        for a in r['internal']['personal_assessments']:
            self.assertEqual(a['assessment_coverage']['assessed_count'],3)
            self.assertTrue(a['assessment_coverage']['minimum_met'])
            self.assertTrue(all(c['value'] is None and c['contribution_points']==0 for c in a['components'][1:]))
            self.assertEqual(len(a['evidence_kinds']['self_report']),3)
        self.assertNotIn('internal_index',json.dumps(public_recommendation(r)))

    def test_no_title_interest_importance_or_unreviewed_claim_imputes_ability(self):
        p=feedback(synthetic_profile(),self.roles[0]['role_id'],'interested')
        r=self.result(p);self.assertEqual(r['public']['coverage']['assessed'],0)
        self.assertTrue(r['public']['targeted_questions'])
        self.assertTrue(all(o['rank'] is None for o in r['public']['options']))
        self.assertEqual(self.result(anchored_profile(levels=(2,4)))['public']['coverage']['assessed'],0)
        for field,value in [('unit','onet:IM'),('provenance','document-claim'),('kind','reviewed_assessment')]:
            p=anchored_profile()
            if field=='provenance':p['evidence'][0]['provenance']['evidence_type']=value
            elif field=='kind':p['evidence'][0]['assessment']['kind']=value
            else:p['evidence'][0][field]=value
            self.assertEqual(self.result(p)['public']['coverage']['assessed'],0)

    def test_zero_conflicts_and_duplicate_observations(self):
        r=self.result(anchored_profile(levels=(0,0,0)))
        self.assertEqual(r['public']['coverage']['assessed'],3)
        self.assertTrue(all(o['personal_score']==0 for o in r['public']['options']))
        p=anchored_profile();e=copy.deepcopy(p['evidence'][0]);e['evidence_id']='another';p['evidence'].append(e)
        self.assertEqual(self.result(p)['internal']['personal_assessments'][0]['assessment_coverage']['assessed_count'],3)
        e['value']=6;self.assertEqual(self.result(p)['public']['coverage']['assessed'],0)
        self.assertTrue(any('Conflicting' in g['reason'] for g in self.result(p)['internal']['personal_assessments'][0]['gaps']))

    def test_negative_idempotent_reset_preserves_skills_and_market(self):
        p=anchored_profile();before=self.result(p,self.market);rid=self.roles[0]['role_id']
        marked=feedback(p,rid,'not_interested');self.assertEqual(marked,feedback(marked,rid,'not_interested'))
        after=self.result(marked,self.market)
        a,b=before['internal']['personal_assessments'][0],after['internal']['personal_assessments'][0]
        self.assertAlmostEqual(a['score']-b['score'],5)
        self.assertEqual(a['components'][0],b['components'][0]);self.assertEqual(a['gaps'],b['gaps'])
        self.assertEqual(before['internal']['current_market'],after['internal']['current_market'])
        self.assertEqual(before['public']['candidate_ids'],after['public']['candidate_ids'])
        reset=feedback(marked,rid,'unknown');self.assertEqual(p['evidence'],reset['evidence'])
        self.assertEqual(self.result(reset,self.market)['public']['options'],before['public']['options'])

    def test_background_interest_workstyle_independent_and_cross_industry_retained(self):
        p=anchored_profile('career_switcher');role=self.roles[0];iid=role['industry_mappings'][0]['target_id']
        optional(p,iid,'transferable_background',1);p=feedback(p,iid,'interested','industry')
        optional(p,role['work_style_mappings'][0]['target_id'],'work_style_preference',1)
        a=self.result(p)['internal']['personal_assessments'][0]
        self.assertEqual([c['contribution_points'] for c in a['components'][1:]],[5,5,0,5])
        p=feedback(p,iid,'not_interested','industry');r=self.result(p)
        self.assertEqual(r['public']['coverage']['candidates'],3)
        self.assertGreaterEqual(sum(c['contribution_points'] for c in r['internal']['personal_assessments'][0]['components'][1:3]),0)

    def test_only_explicit_restrictions_exclude_time_not_fit(self):
        p=anchored_profile();p['constraints']=[dict(constraint_id='limit',scope='role_denylist',hard=True,
            value=json.dumps([self.roles[0]['role_id']]),unit='role_ids_json',evidence_id='fictional')]
        r=self.result(p);self.assertEqual(r['public']['coverage']['excluded'],1)
        p['constraints'][0].update(scope='weekly_hours',value=1,unit='hours');r=self.result(p)
        self.assertEqual(r['public']['coverage']['excluded'],0)
        self.assertEqual(r['internal']['personal_assessments'][0]['score'],self.result()['internal']['personal_assessments'][0]['score'])

    def test_market_can_reverse_order_without_forecast(self):
        parent=self.market;roles=self.roles
        class Counterfactual:
            snapshot=parent.snapshot
            favored=None
            def current(self,kind,rid,*,as_of):
                r=parent.current(kind,rid,as_of=as_of)
                if rid in [x['role_id'] for x in roles[:2]]:r['value']=155 if rid==self.favored else 0
                return r
            def forecast(self,*args,**kwargs):raise ValueError('forecast_unavailable')
        m=Counterfactual();m.favored=roles[0]['role_id'];a=self.result(anchored_profile(levels=(6,6,6)),market=m)
        m.favored=roles[1]['role_id'];b=self.result(anchored_profile(levels=(6,6,6)),market=m)
        self.assertEqual(a['public']['ranking_groups'][0]['role_ids'][0],roles[0]['role_id'])
        self.assertEqual(b['public']['ranking_groups'][0]['role_ids'][0],roles[1]['role_id'])
        self.assertEqual(a['public']['coverage']['current_comparable_ranked'],2)
        self.assertEqual(a['public']['coverage']['personal_only_ranked'],1)
        self.assertEqual(a['public']['status'],'partial')
        self.assertTrue(all(f['status']=='unavailable' for f in a['internal']['forecast_market']))
        self.assertEqual(a['internal']['personal_assessments'],b['internal']['personal_assessments'])

    def test_unknown_market_not_zero_and_distinct_periods_not_compared(self):
        r=self.result(market=self.market)
        self.assertEqual(r['public']['coverage']['current_comparable_ranked'],2)
        self.assertIsNone(r['internal']['current_market'][2]['value'])
        self.assertEqual(r['internal']['current_market'][1]['value'],0)
        parent=self.market;roles=self.roles
        class M:
            snapshot=parent.snapshot
            forecast=parent.forecast
            def current(self,kind,rid,*,as_of):
                r=parent.current(kind,rid,as_of=as_of)
                if rid==roles[1]['role_id']:r['observation_period']={'start':'2026-10-01','end':'2026-10-01'}
                return r
        self.assertEqual(self.result(market=M())['public']['coverage']['current_comparable_ranked'],0)

    def test_no_learned_activation_and_original_proposal_stays_pending(self):
        for kind in ('ridge','xgboost'):
            r=self.result(scorer_kind=kind);self.assertEqual(r['public']['coverage']['assessed'],0)
            self.assertTrue(all(a['score_status']=='model_not_ready' for a in r['internal']['personal_assessments']))
        old=json.loads((ROOT/'ml/configs/intelligence/role-fit.v2.proposed.json').read_text())
        self.assertEqual(old['status'],'pending');self.assertFalse(old['active'])
        self.assertEqual(self.result()['public']['policy_version'],POLICY_ID)

if __name__=='__main__':unittest.main()
