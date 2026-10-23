"""Typed source scope and ranking regressions; fixtures do not establish accuracy."""
import copy
import json
import math
import unittest

from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.integration_cli import role_aliases,provisional_demo_profile
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.market_evidence import EvidenceContext,PREVIOUS_POLICY,evidence_statements,public_trace
from minder_ml.intelligence.role_fit import RoleFitService,LEGACY_MARKET_POLICY
from minder_ml.intelligence.personal_service import update_preference
from minder_ml.intelligence.service_contracts import validate,public_recommendation

STAMP='2026-10-24T00:00:00Z'


class TypedMarketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=OccupationalCatalogue();cls.market=MarketEvidenceService(aliases={'role':role_aliases(cls.cat)})
        cls.roles=[cls.cat.role(x) for x in ('onet:15-1252.00','onet:13-2011.00','onet:11-1011.00','onet:15-2051.00','onet:17-2112.00')]

    def assess(self,profile=None,roles=None,**kw):
        kw.setdefault('market_period_policy_key',PREVIOUS_POLICY)  # freeze v2 treatment regressions
        return RoleFitService(self.market,as_of=STAMP).assess(profile or provisional_demo_profile(),roles or self.roles,**kw)

    def test_before_after_preserves_personal_five_comparable_three_published_two_employer(self):
        before=self.assess(market_period_policy_key=LEGACY_MARKET_POLICY);after=self.assess()
        self.assertEqual(before['internal']['personal_assessments'],after['internal']['personal_assessments'])
        self.assertEqual(before['internal']['current_market'],after['internal']['current_market'])
        self.assertEqual(before['public']['coverage']['current_comparable_ranked'],4)
        c=after['public']['coverage'];self.assertEqual(c['current_comparable_ranked'],5)
        self.assertEqual(c['employer_comparable_ranked'],2);self.assertEqual(c['published_offering_comparable_ranked'],3)
        self.assertEqual(c['sector_context_supported'],5);self.assertEqual(c['shortage_supported'],0)
        self.assertFalse(after['public']['overall_ranking_complete']);self.assertEqual(after['public']['status'],'partial')
        self.assertEqual(after['public']['market_period_policy_key'],PREVIOUS_POLICY)

    def test_actual_quantities_never_added_and_internal_matrix_excluded(self):
        r=self.assess();records=[x for x in r['internal']['evidence_records'] if x['role_id']=='onet:15-1252.00']
        e=next(x for x in records if x['measurement_type']=='employer_observation')
        p=next(x for x in records if x['measurement_type']=='published_offering_activity')
        self.assertEqual((e['value'],p['value']),(5,19899));self.assertNotEqual(e['unit'],p['unit'])
        self.assertNotEqual(e['observation_period'],p['observation_period'])
        self.assertNotEqual(e['source_universe_id'],p['source_universe_id'])
        public=json.dumps(public_recommendation(r))
        for field in ('internal_index','current_index','current_points','final_internal_score'):
            self.assertNotIn(field,public)
        self.assertTrue(all(o['trace_id'] and o['evidence_refs'] for o in r['public']['options']))

    def test_shortage_absence_is_unknown_not_proven_absence(self):
        r=self.assess();rows=[x for x in r['internal']['evidence_records'] if x['measurement_type']=='occupation_shortage']
        self.assertTrue(all(x['value'] is None and x['status']=='unavailable' for x in rows))
        self.assertTrue(all(t['shortage_points']==0 for t in r['internal']['recommendation_traces']))

    def test_grounding_interface_excludes_private_statements_and_internal_arithmetic(self):
        p=provisional_demo_profile();p['evidence'][0]['assessment']['statement']='PRIVATE-PROFILE-SENTINEL activity and personal evidence should stay outside source facts.'
        r=self.assess(p);facts=evidence_statements(r,[self.roles[0]['role_id']])
        self.assertEqual(len(facts),4)
        rendered=json.dumps(facts+[public_trace(r['internal']['recommendation_traces'][0])])
        for forbidden in ('PRIVATE-PROFILE-SENTINEL','current_index','final_internal_score','current_points'):
            self.assertNotIn(forbidden,rendered)
        self.assertTrue(all(f['evidence_id'] for f in facts))

    def test_complete_scoped_comparison_does_not_keep_stale_partial_message(self):
        r=self.assess(roles=self.roles[:3])
        self.assertTrue(r['public']['overall_ranking_complete'])
        self.assertEqual(r['public']['status'],'available')
        self.assertFalse(any(t.startswith('Partial market') for t in r['public']['limitations']))

    def test_sector_context_cannot_masquerade_as_detailed_role_demand(self):
        rows=self.assess()['internal']['evidence_records'];row=copy.deepcopy(next(x for x in rows if x['measurement_type']=='sector_context'))
        self.assertEqual(row['ranking_eligibility'],'context_only')
        self.assertIn('no narrow-role',row['limitations'][0])
        row['ranking_eligibility']='employer_comparable'
        with self.assertRaisesRegex(ValueError,'sector totals'):validate('MarketEvidence',row)

    def test_incomplete_profile_keeps_source_context_without_skill_imputation(self):
        r=self.assess(provisional_demo_profile('incomplete',(2,)))
        self.assertEqual(r['public']['coverage']['assessed'],0)
        self.assertTrue(r['public']['targeted_questions'])
        self.assertTrue(all(o['rank'] is None for o in r['public']['options']))
        self.assertGreater(r['public']['coverage']['sector_context_supported'],0)

    def test_feedback_reset_idempotence_preserves_typed_external_records(self):
        p=provisional_demo_profile();a=self.assess(p)
        def change(p,state):return update_preference(p,entity_type='role',entity_id=self.roles[0]['role_id'],state=state,
            expected_profile_version=p['version'],authorizing_request_id='fictional-explicit-feedback')
        n=change(p,'not_interested');self.assertEqual(n,change(n,'not_interested'));b=self.assess(n)
        self.assertEqual(a['internal']['evidence_records'],b['internal']['evidence_records'])
        self.assertAlmostEqual(a['internal']['personal_assessments'][0]['score']-b['internal']['personal_assessments'][0]['score'],5)
        restored=self.assess(change(n,'unknown'))
        # Trace identity follows the new saved profile version; scores/order reset.
        omit_trace=lambda rows:[{k:v for k,v in row.items() if k!='trace_id'} for row in rows]
        self.assertEqual(omit_trace(a['public']['options']),omit_trace(restored['public']['options']))

    def test_old_role_period_context_does_not_enter_latest_comparison(self):
        role=self.cat.role('onet:27-3031.00');r=self.assess(roles=self.roles+[role])
        rows=[x for x in r['internal']['evidence_records'] if x['role_id']==role['role_id'] and x['measurement_type']=='published_offering_activity']
        self.assertEqual(rows[0]['observation_period']['end'],'2024-12-31')
        self.assertEqual(rows[0]['ranking_eligibility'],'context_only')
        o=next(x for x in r['public']['options'] if x['role_id']==role['role_id'])
        self.assertEqual(o['ranking_basis'],'personal_only_market_unsupported')

    def test_source_normalization_stable_when_view_changes(self):
        full=self.assess();small=self.assess(roles=self.roles[:3])
        def trace(r,rid):return next(t for t in r['internal']['recommendation_traces'] if t['role_id']==rid)
        for role in self.roles[:3]:
            a,b=trace(full,role['role_id']),trace(small,role['role_id'])
            self.assertEqual(a['normalization_denominator'],40640)
            self.assertEqual(a['current_index'],b['current_index'])
            self.assertAlmostEqual(a['current_index'],100*math.log1p(next(x['value'] for x in full['internal']['evidence_records'] if x['role_id']==role['role_id'] and x['measurement_type']=='published_offering_activity'))/math.log1p(40640))

    def test_future_source_record_cannot_leak_from_newer_collection(self):
        service=RoleFitService(self.market,as_of='2026-10-23T00:00:00Z')
        r=service.assess(provisional_demo_profile(),self.roles)
        self.assertEqual(r['public']['coverage']['current_comparable_ranked'],0)
        self.assertTrue(all(x['status']=='unavailable' for x in r['internal']['evidence_records'] if x['measurement_type'] in ('published_offering_activity','employer_observation')))

    def test_positive_shortage_fixture_is_bounded_not_frequency(self):
        # Explicit fictional software check of future handoff handling; no real shortage result claimed.
        parent=self.market
        class FictionalShortage:
            def __getattr__(self,k):return getattr(parent,k)
            def shortage_observations(self,*,as_of):
                source=parent.published_roles['observations'][0]
                return [dict(entity_id='fictional:shortage-role',value=1,source_id='fictional-shortage-fixture',
                    source_version='f'*64,source_document_sha256='f'*64,source_url='https://example.com/fictional-shortage',
                    available_at=source['available_at'],published_at=source['published_at'],period=source['period'],source_universe_id='fictional-fixture-only')]
        baseline=RoleFitService(parent,as_of=STAMP).assess(provisional_demo_profile(),self.roles,market_period_policy_key=LEGACY_MARKET_POLICY)
        ctx=EvidenceContext(FictionalShortage(),policy_version=PREVIOUS_POLICY);ctx.links['shortage_roles']=[dict(role_id=self.roles[0]['role_id'],source_entity_id='fictional:shortage-role',relation='source_label_equivalence',scope='Explicitly fictional unit fixture.')]
        r=ctx.apply(baseline,self.roles,STAMP)
        t=next(t for t in r['internal']['recommendation_traces'] if t['role_id']==self.roles[0]['role_id'])
        self.assertEqual(t['shortage_points'],2);self.assertEqual(r['public']['coverage']['shortage_supported'],1)
        bad=copy.deepcopy(next(x for x in r['internal']['evidence_records'] if x['measurement_type']=='occupation_shortage' and x['status']=='available'));bad['value']=0
        with self.assertRaisesRegex(ValueError,'unlisted is unknown'):validate('MarketEvidence',bad)



class CodedShortageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=OccupationalCatalogue();cls.market=MarketEvidenceService(aliases={'role':role_aliases(cls.cat)})
        cls.codes=['onet:11-3031.00','onet:15-1252.00','onet:17-2112.00','onet:29-1051.00','onet:29-1171.00','onet:49-9081.00','onet:53-3032.00']
        cls.roles=[cls.cat.role(r) for r in cls.codes]

    def assess(self,profile=None,roles=None,**kw):
        return RoleFitService(self.market,as_of=STAMP).assess(profile or provisional_demo_profile(),roles or self.roles,**kw)

    def test_actual_designations_are_related_context_with_unknown_publication_dates(self):
        r=self.assess();c=r['public']['coverage']
        self.assertEqual(c['shortage_supported'],7);self.assertEqual(c['shortage_context_supported'],7)
        self.assertEqual(c['shortage_exact_role_supported'],0)
        rows=[e for e in r['internal']['evidence_records'] if e['measurement_type']=='occupation_shortage']
        for e in rows:
            self.assertEqual(e['status'],'available');self.assertEqual(e['value'],1)
            self.assertEqual(e['source_value'],'listed_in_national_MyCOL')
            self.assertEqual(e['mapping']['relation'],'code_bridge_context')
            self.assertEqual(e['mapping']['bridge']['match_type'],'exactISCO')
            self.assertIsNone(e['published_at']);self.assertIsNone(e['observation_period']['start'])
            self.assertIn('2024/2025',e['observation_period']['label'])
            self.assertTrue(e['source_record_refs']);self.assertIn('not proof',e['mapping']['scope'])
        self.assertTrue(all(t['shortage_points']==1 for t in r['internal']['recommendation_traces']))

    def test_personal_fit_unchanged_and_bounded_context_not_frequency(self):
        before=self.assess(market_period_policy_key=PREVIOUS_POLICY);after=self.assess()
        self.assertEqual(before['internal']['personal_assessments'],after['internal']['personal_assessments'])
        self.assertEqual(before['internal']['current_market'],after['internal']['current_market'])
        self.assertEqual(after['public']['market_period_policy_key'],'personal-current-evidence-v2.1')
        for t in after['internal']['recommendation_traces']:
            self.assertGreaterEqual(t['final_internal_score'],0);self.assertLessEqual(t['final_internal_score'],100)

    def test_available_employer_comparison_not_stranded_by_published_singleton(self):
        roles=[self.cat.role(r) for r in ('onet:15-1252.00','onet:17-2112.00','onet:11-3031.00')]
        r=self.assess(roles=roles)
        self.assertEqual(r['public']['coverage']['employer_comparable_ranked'],2)
        self.assertEqual(r['public']['coverage']['current_comparable_ranked'],2)
        # Also prefer a three-role employer comparison over a two-role published
        # comparison that would strand the remaining known employer role.
        roles=[self.cat.role(r) for r in ('onet:15-1252.00','onet:13-2011.00','onet:15-2051.00')]
        r=self.assess(roles=roles)
        self.assertEqual(r['public']['coverage']['current_comparable_ranked'],3)
        self.assertEqual(r['public']['coverage']['employer_comparable_ranked'],3)

    def test_no_missing_critical_flag_or_inferred_unlisted_six_digit_scope(self):
        r=self.assess(roles=[self.cat.role('onet:15-2051.00')])
        row=next(e for e in r['internal']['evidence_records'] if e['measurement_type']=='occupation_shortage')
        self.assertEqual(row['status'],'unavailable');self.assertIsNone(row['value'])
        self.assertEqual(r['public']['coverage']['shortage_supported'],0)
        query=self.market.current_context(as_of=STAMP,occupation_system='MASCO',occupation_version='2020',occupation_code='2512-99')
        self.assertEqual(query['status'],'unknown');self.assertEqual(query['records'],[])

    def test_incomplete_profile_gets_no_rank_despite_real_shortage_context(self):
        r=self.assess(provisional_demo_profile('incomplete',(2,)))
        self.assertEqual(r['public']['coverage']['assessed'],0)
        self.assertEqual(r['public']['coverage']['shortage_supported'],7)
        self.assertEqual(r['public']['coverage']['shortage_adjusted_ranked'],0)
        self.assertTrue(all(o['rank'] is None for o in r['public']['options']))



class PassageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=OccupationalCatalogue();cls.market=MarketEvidenceService(aliases={'role':role_aliases(cls.cat)})
        cls.role=cls.cat.role('onet:15-1252.00')

    def payloads(self):
        from minder_ml.intelligence.market_evidence import make_source_passage
        ctx=EvidenceContext(self.market)
        current=self.market.current('role',self.role['role_id'],as_of=STAMP)
        return ctx,[make_source_passage(r) for r in ctx.records(self.role,STAMP,current)]

    def test_real_four_families_recomputed_and_null_dates_preserved(self):
        ctx,rows=self.payloads();self.assertEqual({r['record']['measurement_type'] for r in rows},{'occupation_shortage','published_offering_activity','employer_observation','sector_context'})
        for p in rows:self.assertEqual(p,ctx.verify_passage(p,self.role,checked_at=STAMP))
        shortage=next(p for p in rows if p['record']['measurement_type']=='occupation_shortage')
        self.assertIn('Publication date not verified',shortage['canonical_passage'])
        self.assertNotIn('personal_score',json.dumps(rows));self.assertNotIn('current_index',json.dumps(rows))

    def test_good_hash_and_valid_id_cannot_launder_wrong_number_scope_date_or_citation(self):
        from minder_ml.intelligence.market_evidence import make_source_passage
        ctx,rows=self.payloads();p=next(p for p in rows if p['record']['measurement_type']=='published_offering_activity')
        for mutator in (lambda r:r.update(value=r['value']+1),lambda r:r['mapping'].update(scope='All Malaysian jobs and guaranteed hiring.'),
                        lambda r:r['source'].update(uri='https://example.com/unrelated'),lambda r:r.update(published_at='2026-01-01T00:00:00Z')):
            r=copy.deepcopy(p['record']);mutator(r);forged=make_source_passage(r)
            with self.assertRaises(ValueError):ctx.verify_passage(forged,self.role,checked_at=STAMP)

    def test_wrong_role_or_future_issue_rejected(self):
        ctx,rows=self.payloads()
        with self.assertRaises(ValueError):ctx.verify_passage(rows[0],self.cat.role('onet:11-1011.00'),checked_at=STAMP)
        with self.assertRaisesRegex(ValueError,'future'):ctx.verify_passage(rows[0],self.role,checked_at='2026-10-23T00:00:00Z')

    def test_modified_adapter_memory_is_not_valid_pinned_source(self):
        parent=copy.copy(self.market);parent.published_roles=copy.deepcopy(parent.published_roles)
        next(r for r in parent.published_roles['observations'] if r['entity_id'].endswith('software-developers'))['value']+=1
        ctx=EvidenceContext(parent)
        from minder_ml.intelligence.market_evidence import make_source_passage
        row=next(r for r in ctx.records(self.role,STAMP) if r['measurement_type']=='published_offering_activity')
        with self.assertRaisesRegex(ValueError,'integrity'):ctx.verify_passage(make_source_passage(row),self.role,checked_at=STAMP)

if __name__=='__main__':unittest.main()
