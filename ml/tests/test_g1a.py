"""Synthetic contract fixtures, never occupation facts or human-reviewed labels."""
import copy
import json
import unittest
from minder_ml.intelligence.policy import load_policy, fingerprint
from minder_ml.intelligence.policy_features import derive_features, validate_milestone
from minder_ml.intelligence.inference import recommend_profile
from minder_ml.intelligence.policy_sources import native_catalogue


def fixture():
    profile = {'profile_id': 'synthetic-contract-only', 'version': 'test-v1',
               'data_class': 'synthetic', 'planning_horizon': {'weeks': 12}, 'hours_per_week': 1}
    milestone = {'milestone_id': 'synthetic-only', 'version': 'test-v1', 'scope': 'initial_preparation',
        'target_artifact': 'Synthetic contract exercise, no occupational claim',
        'role_id': 'synthetic-role', 'provenance_class': 'policy-derived',
        'derivation_rule_id': 'G1A-SYNTHETIC-CONTRACT-FIXTURE',
        'status': 'policy_accepted', 'acceptance': {'source_id': 'synthetic-test-only'},
        'criteria': [{'criterion_id': 'c', 'anchors': {'0': 'unmet', '0.5': 'partially met', '1': 'fully met'},
                      'anchor_version': 'a1', 'evidence_ids': ['synthetic-definition']}],
        'interest_tags': [{'tag_id': 'i', 'evidence_ids': ['synthetic-definition']}],
        'work_style_tags': [{'tag_id': 'w', 'evidence_ids': ['synthetic-definition']}],
        'resource_groups': [], 'hard_requirements': [],
        'tasks': [{'task_id': 'prereq', 'version': 'v1', 'prerequisites': [],
                   'evidence_ids': ['synthetic-definition'],
                   'effort': {'low': 6, 'high': 12, 'unit': 'hours', 'basis': 'synthetic test estimate', 'evidence_ids': ['synthetic-estimate']}},
                  {'task_id': 'main', 'version': 'v1', 'prerequisites': ['prereq'],
                   'evidence_ids': ['synthetic-definition'],
                   'effort': {'low': 6, 'high': 12, 'unit': 'hours', 'basis': 'synthetic test estimate', 'evidence_ids': ['synthetic-estimate']}}]}
    role = {'role_id': 'synthetic-role', 'version': 'test-v1', 'milestone': milestone}
    answers = {'profile_version': 'test-v1', 'milestone_version': 'test-v1', 'criterion_assessments': [{'criterion_id': 'c', 'milestone_version': 'test-v1',
                'anchor_version': 'a1', 'value': 0, 'basis': 'anchored_self_report', 'evidence_ids': ['synthetic-answer']}],
               'interest_tags': [{'tag_id': 'i', 'value': 'interested', 'evidence_ids': ['synthetic-answer']}],
               'work_style_tags': [{'tag_id': 'w', 'value': 'no_preference', 'evidence_ids': ['synthetic-answer']}]}
    return profile, role, answers


class G1ATests(unittest.TestCase):
    def setUp(self):
        # Numerical kernel tests vary fixtures in memory; acceptance integrity is
        # separately exercised without this isolated seam below.
        from unittest.mock import patch
        self.acceptance = patch('minder_ml.intelligence.policy_sources.verify_milestone_acceptance', return_value=True)
        self.acceptance.start()
        self.addCleanup(self.acceptance.stop)

    def test_policy_exact_and_native(self):
        cfg, active = load_policy()
        self.assertEqual(cfg['features']['weights'], [.4,.2,.2,.1,.1])
        self.assertEqual(cfg['approval']['reviewer_id'], None)
        roles = native_catalogue()
        self.assertEqual(len(roles), 3)
        self.assertTrue(all(r['status'] == 'policy_accepted' and r['milestone'] is None for r in roles))
        self.assertTrue(all(r['identifier']['taxonomy_edition'] is None for r in roles))

    def test_zero_unknown_and_anchor_version(self):
        p,r,a = fixture()
        d = derive_features(p,r,a)
        self.assertEqual(d['feature_components']['skill_coverage'], 0)
        self.assertEqual(d['assessed_requirement_fraction'], 1)
        self.assertEqual(d['criterion_gaps'][0]['remaining_fraction'], 1)
        a['criterion_assessments'][0]['anchor_version'] = 'stale'
        d = derive_features(p,r,a)
        self.assertIsNone(d['feature_components']['skill_coverage'])
        self.assertEqual(d['assessed_requirement_fraction'], 0)
        self.assertIsNone(d['criterion_gaps'][0]['remaining_fraction'])

    def test_invalid_catalogue_not_person_failure(self):
        p,r,a = fixture(); r['milestone']['criteria'] = []
        d=derive_features(p,r,a)
        self.assertEqual(d['catalogue_status'], 'invalid_catalogue')
        self.assertIsNone(d['assessed_requirement_fraction'])
        r['milestone'] = None
        self.assertIsNone(derive_features(p,r,a)['assessed_requirement_fraction'])

    def test_effort_closure_completion_and_boundaries(self):
        p,r,a=fixture(); d=derive_features(p,r,a)
        self.assertEqual(d['traces']['T']['effort_high'],24)
        self.assertEqual(d['feature_components']['time_feasibility'],.5)
        self.assertEqual(d['traces']['T']['T_high'],1)
        a['completed_tasks']=[{'task_id':'prereq','task_version':'v1','completed':True,'evidence_ids':['done']}]
        self.assertEqual(derive_features(p,r,a)['traces']['T']['effort_high'],12)
        a['completed_tasks'].append({'task_id':'main','task_version':'v1','completed':True,'evidence_ids':['done']})
        p['hours_per_week']=None
        self.assertEqual(derive_features(p,r,a)['feature_components']['time_feasibility'],1)
        r['milestone']['tasks'][0]['prerequisites']=['main']
        with self.assertRaises(ValueError): validate_milestone(r['milestone'])

    def test_unknown_effort_and_invalid_input(self):
        p,r,a=fixture(); r['milestone']['tasks'][0]['effort']=None
        self.assertIsNone(derive_features(p,r,a)['feature_components']['time_feasibility'])
        p['hours_per_week']=-1
        with self.assertRaises(ValueError): derive_features(p,r,a)

    def test_resources_or_groups_unknown_and_budget(self):
        p,r,a=fixture()
        r['milestone']['resource_groups']=[{'group_id':'g','evidence_ids':['def'],
            'alternatives':[{'alternative_id':'x'},{'alternative_id':'y'}]}]
        self.assertIsNone(derive_features(p,r,a)['feature_components']['resource_feasibility'])
        a['resources']=[{'alternative_id':'x','value':'unavailable','evidence_ids':['ans']},
                        {'alternative_id':'y','value':'accessible','evidence_ids':['ans']}]
        self.assertEqual(derive_features(p,r,a)['feature_components']['resource_feasibility'],1)
        a['resources'][1]['value']='unavailable'
        self.assertEqual(derive_features(p,r,a)['feature_components']['resource_feasibility'],0)
        r['milestone']['resource_groups'][0]['alternatives'][1].update(cost=10,currency='MYR',period='milestone')
        a['resources'][1]['value']='accessible'
        a['budget']={'amount':20,'currency':'USD','period':'milestone','evidence_ids':['budget']}
        self.assertIsNone(derive_features(p,r,a)['feature_components']['resource_feasibility'])

    def test_constraints_do_not_rank_unknown_or_conflict(self):
        p,r,a=fixture()
        r['milestone']['hard_requirements']=[{'requirement_id':'access','evidence_ids':['def']}]
        d=derive_features(p,r,a); self.assertEqual(d['constraint_status'],'needs_check')
        a['constraint_checks']=[{'requirement_id':'access','value':'conflict','constraint_id':'u','evidence_ids':['ans']}]
        self.assertEqual(derive_features(p,r,a)['constraint_status'],'needs_check')
        a['hard_constraints']=[{'constraint_id':'u','statement':'Synthetic explicit access constraint', 'declared_by_user':True,'evidence_ids':['synthetic-user-answer']}]
        out=recommend_profile(p,[r],answers_by_role={r['role_id']:a})
        self.assertEqual(out['derivations'][0]['constraint_status'],'excluded')
        self.assertEqual(out['recommendation']['options'],[])

    def test_service_determinism_invalidation_and_contract(self):
        p,r,a=fixture()
        out=recommend_profile(p,[r],answers_by_role={r['role_id']:a})
        self.assertEqual(out,recommend_profile(p,[r],answers_by_role={r['role_id']:a}))
        self.assertEqual(out['recommendation']['options'][0]['personal_fit_index'],45)
        self.assertEqual(out['recommendation']['result_schema_version'],'minder-recommendation-v1')
        self.assertEqual(sum(out['derivations'][0]['traces']['baseline']['contributions'].values()),45)
        p['version']='changed'
        self.assertNotEqual(out['input_fingerprint'],recommend_profile(p,[r],answers_by_role={r['role_id']:a})['input_fingerprint'])
        a['interest_tags']=[]
        self.assertFalse(derive_features(p,r,a)['eligible'])
        self.assertIsNone(derive_features(p,r,a)['feature_components']['interest_alignment'])

    def test_missing_assessment_evidence_rejected(self):
        p,r,a=fixture(); a['criterion_assessments'][0]['evidence_ids']=[]
        with self.assertRaises(ValueError): derive_features(p,r,a)
        a['criterion_assessments'][0]['evidence_ids']=['ans']; a['criterion_assessments'][0]['value']=.6
        with self.assertRaises(ValueError): derive_features(p,r,a)


class SourceIntegrityTests(unittest.TestCase):
    def test_acceptance_integrity_and_fixture_service(self):
        from minder_ml.intelligence.policy import ROOT
        from minder_ml.intelligence.policy_sources import accept_milestone, verify_milestone_acceptance
        registry=json.loads((ROOT/'ml/configs/intelligence/measurement_sources.v1.json').read_text())['sources'][0]
        raw=json.loads((ROOT/registry['source_path']).read_text())
        m=accept_milestone(registry['source_path'],registry['sha256'],'synthetic-only',
                           source_id=registry['source_id'],source_version=registry['source_version'],
                           provenance_class='policy-derived')
        self.assertTrue(verify_milestone_acceptance(m))
        role={'role_id':'synthetic-role','version':'test-v1','milestone':m}
        out=recommend_profile(raw['profile'],[role],answers_by_role={'synthetic-role':raw['answers']})
        self.assertEqual(out['recommendation']['options'][0]['personal_fit_index'],45)
        m['criteria'][0]['anchors']['1']='tampered'
        self.assertFalse(derive_features(raw['profile'],role,raw['answers'])['eligible'])
        with self.assertRaises(ValueError):
            accept_milestone(registry['source_path'],'0'*64,'synthetic-only',
                source_id=registry['source_id'],source_version=registry['source_version'])
        with self.assertRaises(ValueError):
            accept_milestone(registry['source_path'],registry['sha256'],'synthetic-only',
                source_id=registry['source_id'],source_version=registry['source_version'],provenance_class='llm-proposed')

class AdditionalPolicyTests(unittest.TestCase):
    setUp = G1ATests.setUp
    def test_work_utility_exact_policy(self):
        p,r,a=fixture()
        for value, expected in [('compatible',1),('acceptable',.5),('no_preference',.5),('incompatible',0)]:
            a['work_style_tags'][0]['value']=value
            self.assertEqual(derive_features(p,r,a)['feature_components']['work_style_alignment'],expected)

    def test_equal_criterion_weights_and_partial_q(self):
        p,r,a=fixture()
        second=copy.deepcopy(r['milestone']['criteria'][0]); second['criterion_id']='c2'
        r['milestone']['criteria'].append(second)
        d=derive_features(p,r,a)
        self.assertEqual(d['assessed_requirement_fraction'],.5)
        self.assertEqual(d['feature_components']['skill_coverage'],0)
        self.assertIn('incomplete_skill_evidence',d['exceptions'])
        self.assertFalse(d['eligible'])

    def test_content_fingerprint_invalidates_all_dependencies(self):
        p,r,a=fixture(); original=derive_features(p,r,a)['input_fingerprint']
        for kind in ('profile','criterion','effort','utility','evidence'):
            p1,r1,a1=copy.deepcopy((p,r,a))
            if kind=='profile': p1['hours_per_week']=2
            if kind=='criterion': r1['milestone']['criteria'][0]['anchors']['1']='different full anchor'
            if kind=='effort': r1['milestone']['tasks'][0]['effort']['high']=13
            if kind=='utility': a1['interest_tags'][0]['value']='avoid'
            if kind=='evidence': a1['criterion_assessments'][0]['evidence_ids']=['new evidence']
            self.assertNotEqual(original,derive_features(p1,r1,a1)['input_fingerprint'])

    def test_golden_and_contract_and_no_learner_fallback(self):
        from minder_ml.intelligence.schemas import FeatureSnapshot
        from minder_ml.intelligence.scoring import baseline
        self.assertEqual(baseline(FeatureSnapshot(.6,.8,.5,1,.7,1)),67)
        p,r,a=fixture()
        result=recommend_profile(p,[r],answers_by_role={r['role_id']:a},scorer_kind='ridge')
        self.assertEqual(result['recommendation']['result_kind'],'model_not_ready')
        self.assertNotIn('baseline',result['derivations'][0]['traces'])
        import jsonschema
        from minder_ml.intelligence.policy import ROOT
        schema=json.loads((ROOT/'contracts/policy-recommendation.g1a.v1.schema.json').read_text())
        jsonschema.Draft202012Validator(schema).validate(result)

class RemainingBoundaryTests(unittest.TestCase):
    setUp = G1ATests.setUp

    def test_invalid_resource_cost_and_effort(self):
        p,r,a=fixture()
        r['milestone']['resource_groups']=[{'group_id':'g','evidence_ids':['d'],
            'alternatives':[{'alternative_id':'a','cost':-1,'currency':'MYR','period':'milestone'}]}]
        self.assertEqual(derive_features(p,r,a)['catalogue_status'],'invalid_catalogue')
        r['milestone']['resource_groups']=[]
        r['milestone']['tasks'][0]['effort']['low']=13
        self.assertEqual(derive_features(p,r,a)['catalogue_status'],'invalid_catalogue')

    def test_source_change_changes_key_and_invalidates(self):
        from unittest.mock import patch
        from minder_ml.intelligence.policy import ROOT
        p,r,a=fixture()
        source='ml/tests/fixtures/g1a_contract.synthetic.json'
        import hashlib
        expected=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
        r['sources']=[{'path':source,'sha256':expected}]
        before=derive_features(p,r,a)
        original=type(ROOT).read_bytes
        def changed(path):
            return b'changed-source' if path == (ROOT/source) else original(path)
        with patch.object(type(ROOT),'read_bytes',changed):
            after=derive_features(p,r,a)
        self.assertNotEqual(before['input_fingerprint'],after['input_fingerprint'])
        self.assertIn('source_dependency_changed_or_missing',after['exceptions'])
        self.assertFalse(after['eligible'])

class ReexecutionBoundaryTests(unittest.TestCase):
    setUp = G1ATests.setUp

    def test_catalogue_evidence_references_are_real_id_lists(self):
        p, r, a = fixture()
        for bad in ('not-an-id-list', [''], [None], ['duplicate', 'duplicate']):
            with self.subTest(value=bad):
                r['milestone']['criteria'][0]['evidence_ids'] = bad
                result = derive_features(p, r, a)
                self.assertEqual(result['catalogue_status'], 'invalid_catalogue')
                self.assertIsNone(result['assessed_requirement_fraction'])
                self.assertTrue(result['questions'])

    def test_malformed_task_progress_cannot_remove_effort(self):
        p, r, a = fixture()
        a['completed_tasks'] = [{'task_id': 'prereq', 'task_version': 'v1',
                                 'completed': True, 'evidence_ids': 'truthy-string'}]
        with self.assertRaisesRegex(ValueError, 'evidence_ids'):
            derive_features(p, r, a)
        a['completed_tasks'][0]['evidence_ids'] = []
        result = derive_features(p, r, a)
        self.assertEqual(result['traces']['T']['effort_high'], 24)

    def test_unmapped_user_hard_constraint_remains_needs_check(self):
        p, r, a = fixture()
        a['hard_constraints'] = [{'constraint_id': 'schedule',
            'statement': 'Synthetic user cannot attend weekday daytime sessions',
            'declared_by_user': True, 'evidence_ids': ['synthetic-declaration']}]
        out = recommend_profile(p, [r], answers_by_role={r['role_id']: a})
        self.assertEqual(out['recommendation']['options'], [])
        self.assertEqual(out['derivations'][0]['constraint_status'], 'needs_check')
        self.assertEqual(out['derivations'][0]['feature_components']['skill_coverage'], 0)
        self.assertIn('hard_constraint_needs_check', out['derivations'][0]['exceptions'])

    def test_invalid_catalogue_isolated_from_valid_option(self):
        p, r, a = fixture()
        broken = copy.deepcopy(r)
        broken['role_id'] = 'broken-role'
        broken['milestone']['role_id'] = 'broken-role'
        broken['milestone']['criteria'][0]['evidence_ids'] = 'invalid-reference'
        out = recommend_profile(p, [broken, r], answers_by_role={r['role_id']: a})
        self.assertEqual([o['role_id'] for o in out['recommendation']['options']], ['synthetic-role'])
        self.assertEqual(out['derivations'][0]['catalogue_status'], 'invalid_catalogue')
        self.assertEqual(out['recommendation']['options'][0]['personal_fit_index'], 45)
