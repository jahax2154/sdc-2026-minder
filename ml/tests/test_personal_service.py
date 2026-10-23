"""Initial occupational matching regressions; no empirical validity claims."""
import unittest
import copy
import json
from unittest.mock import patch
from minder_ml.intelligence.policy import ROOT

from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.service_contracts import validate
from minder_ml.intelligence.personal_service import PersonalMatchingService, update_preference, filter_roles
from minder_ml.intelligence.personal_cli import synthetic_profile
from minder_ml.intelligence.personal_training import machinery_plan, grouped_split, load_machinery_candidate, ARTIFACT_ROOT


class CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = OccupationalCatalogue()

    def test_all_source_identities_loaded_without_milestones(self):
        catalogue = self.catalogue
        self.assertEqual(catalogue.coverage['raw_unique_occupations'], len(catalogue.roles()))
        self.assertGreater(len(catalogue.roles(eligible_only=True)), 3)
        self.assertEqual(catalogue.coverage['rejected'], [])
        for role in catalogue.roles():
            self.assertNotIn('milestone', role)
            self.assertEqual(role['taxonomy_version'], '2019')
        validate('Role', catalogue.role('onet:15-1252.00'))

    def test_source_ratings_preserve_scales_flags_and_geography(self):
        catalogue = self.catalogue
        roles = catalogue.roles()
        self.assertTrue(any(r['eligibility'] == 'partial' for r in roles))
        role = catalogue.role('onet:11-1011.00')
        self.assertEqual({r['unit'] for r in role['requirements']}, {'onet:IM', 'onet:LV'})
        self.assertTrue(all(r['provenance']['geography'] == 'US' for r in role['requirements']))
        self.assertTrue(role['industry_mappings'])
        self.assertTrue(all(m['source']['geography'] == 'US' for m in role['industry_mappings']))
        originals = {r['O*NET-SOC Code']: r for r in
                     [catalogue.reference(x['role_id'])['occupation'] for x in roles]}
        self.assertEqual(len(originals), len(roles))
        for role in roles:
            reference = catalogue.reference(role['role_id'])
            usable = {(r['Element ID'], r['Scale ID']) for r in reference['essential_skills']
                      if r['Recommend Suppress'] == 'N' and r['Not Relevant'] in ('', 'N')}
            for evidence in role['requirements']:
                self.assertIn((evidence['subject_id'].removeprefix('onet:element:'),
                               evidence['unit'].removeprefix('onet:')), usable)
        self.assertIn('Hot Technology', catalogue.reference('onet:11-1011.00')['software_examples'][0])


class PersonalServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = OccupationalCatalogue()
        cls.roles = [cls.catalogue.role('onet:15-1252.00'), cls.catalogue.role('onet:11-1011.00')]

    def test_source_requirements_without_milestone_never_become_person_mastery(self):
        profile = synthetic_profile()
        original = copy.deepcopy(profile)
        result = PersonalMatchingService().assess(profile, self.roles)
        self.assertEqual(profile, original)
        self.assertEqual(len(result['public']['candidate_ids']), 2)
        self.assertEqual(result['public']['status'], 'policy_pending')
        for assessment in result['internal']['personal_assessments']:
            self.assertIsNone(assessment['score'])
            self.assertTrue(all(g['state'] == 'unknown' for g in assessment['gaps']))
            self.assertTrue(any(g['evidence_ids'] for g in assessment['gaps']))
            self.assertNotIn('milestone', str(assessment['unknowns']))
        self.assertTrue(all(o['rank'] is None for o in result['public']['options']))
        self.assertEqual(result['internal']['combined_scores'], [])

    def test_industry_history_desire_and_many_to_many_links_do_not_filter(self):
        profile = synthetic_profile('career_switcher')
        source = self.roles[0]['source']
        roles = copy.deepcopy(self.roles)
        roles[0]['industry_mappings'] = [dict(target_id=i, source=source, relation='test-only',
                                              status='source_accepted') for i in ('synthetic:prior-industry', 'other')]
        result = PersonalMatchingService().assess(profile, roles)
        self.assertEqual(len(result['public']['candidate_ids']), 2)
        first = result['internal']['personal_assessments'][0]
        context = {i['industry_id']: i for i in first['industry_contributions']}
        self.assertEqual(context['synthetic:prior-industry']['background_fields'][0]['state'], 'want_to_leave')
        self.assertEqual(set(context), {'synthetic:prior-industry', 'other'})
        self.assertIsNone(context['synthetic:prior-industry']['assessment'])

    def test_policy_or_blend_cannot_be_enabled_by_caller(self):
        service = PersonalMatchingService()
        profile = synthetic_profile()
        with self.assertRaises(ValueError):
            service.assess(synthetic_profile(), self.roles, policy_version='legacy-v1')
        with self.assertRaises(ValueError):
            service.assess(synthetic_profile(), self.roles, market_period_policy_key='current_only')
        with patch('minder_ml.intelligence.personal_service.json.loads', return_value={
                'policy_id':'personal-role-fit-v2-proposal','status':'accepted','active':True}):
            with self.assertRaisesRegex(ValueError, 'explicit approved implementation'):
                service.assess(profile, self.roles)

    def test_committed_c_pending_token_maps_to_canonical_inactive_policy(self):
        from minder_ml.intelligence.app_context import CareerServices
        profile = synthetic_profile()
        result = CareerServices(PersonalMatchingService(), roles=self.roles,
                                mode='local_source_services').career_context(
                                    profile, expected_profile_version=profile['version'])
        self.assertEqual(result['recommendation']['public']['policy_version'], 'personal-role-fit-v2-proposal')
        self.assertEqual(result['recommendation']['public']['status'], 'policy_pending')

    def test_feedback_is_scoped_idempotent_resettable_and_versioned(self):
        profile = synthetic_profile('career_switcher')
        original = copy.deepcopy(profile)
        def change(p, kind='role', target='onet:15-1252.00', state='not_interested'):
            return update_preference(p, entity_type=kind, entity_id=target, state=state,
                                     authorizing_request_id='synthetic-explicit-feedback',
                                     expected_profile_version=p['version'])
        marked = change(profile)
        self.assertEqual(marked, change(marked))
        self.assertEqual(profile, original)
        self.assertNotEqual(marked['version'], profile['version'])
        self.assertEqual(marked['evidence'], original['evidence'])
        self.assertEqual(marked['current_fields'], original['current_fields'])
        both = change(marked, 'industry', 'synthetic:prior-industry')
        reset = change(both, state='unknown')
        self.assertEqual(len(reset['preferences']), 1)
        self.assertEqual(reset['preferences'][0]['entity_type'], 'industry')
        self.assertEqual(reset, change(reset, state='unknown'))
        with self.assertRaisesRegex(ValueError, 'stale_profile_version'):
            update_preference(marked, entity_type='role', entity_id='onet:15-1252.00',
                              state='interested', authorizing_request_id='request',
                              expected_profile_version=profile['version'])
        # Negative preferences do not filter candidates, alter evidence or create scores.
        result = PersonalMatchingService().assess(both, self.roles)
        self.assertEqual(result['public']['candidate_ids'], [r['role_id'] for r in self.roles])
        self.assertEqual(result['internal']['personal_assessments'][0]['role_preference']['state'], 'not_interested')
        self.assertIn('retained for exploration', result['public']['options'][0]['explanation'])

    def test_explicit_filters_are_visible_reversible_and_use_only_accepted_mappings(self):
        roles = copy.deepcopy(self.roles)
        roles[1]['industry_mappings'] = []  # explicit unknown-mapping fixture
        roles[0]['industry_mappings'] = [dict(target_id='i1', source=roles[0]['source'],
                                              relation='synthetic-test', status='pending')]
        restriction = dict(role_ids=None, industry_ids=['i1'], query=None, authorizing_request_id='filter-request')
        pending = filter_roles(roles, restriction)
        self.assertEqual(pending['roles'], [])
        self.assertEqual(len(pending['unresolved_industry_role_ids']), 2)
        roles[0]['industry_mappings'][0]['status'] = 'source_accepted'
        accepted = filter_roles(roles, restriction)
        self.assertEqual(len(accepted['roles']), 1)
        self.assertEqual(accepted['applied_filter'], restriction)
        self.assertEqual(filter_roles(roles)['roles'], roles)
        self.assertEqual(len(roles), 2)
        restriction.update(industry_ids=None, role_ids=[], query=None)
        self.assertEqual(filter_roles(roles, restriction)['roles'], [])
        restriction.update(role_ids=None, query='SOFTWARE')
        self.assertEqual([r['role_id'] for r in filter_roles(roles, restriction)['roles']], ['onet:15-1252.00'])

    def test_market_periods_and_values_survive_feedback_unchanged(self):
        fixture = json.loads((ROOT / 'contracts/fixtures/parallel-v1/forecast_unavailable.json').read_text())['payload']
        class UnavailableMarket:
            def forecast(self, entity_type, entity_id, *, issued_at):
                result = copy.deepcopy(fixture)
                result.update(entity_type=entity_type, entity_id=entity_id, issued_at=issued_at)
                return result
            def current(self, entity_type, entity_id, *, as_of):
                result = self.forecast(entity_type, entity_id, issued_at=as_of)
                result.update(kind='current', target_period=None, horizon='observed')
                return result
        profile = synthetic_profile()
        service = PersonalMatchingService(UnavailableMarket(), as_of='2026-10-23T00:00:00Z')
        before = service.assess(profile, self.roles)
        marked = update_preference(profile, entity_type='role', entity_id=self.roles[0]['role_id'],
                                   state='not_interested', authorizing_request_id='synthetic-request',
                                   expected_profile_version=profile['version'])
        after = service.assess(marked, self.roles)
        for key in ('current_market', 'forecast_market'):
            self.assertEqual(before['internal'][key], after['internal'][key])
            self.assertTrue(all(r['value'] is None for r in after['internal'][key]))
        from minder_ml.intelligence.service_contracts import public_recommendation
        self.assertNotIn('internal_index', json.dumps(public_recommendation(after)))


class LearnerPreparationTests(unittest.TestCase):
    def test_split_freezes_family_groups_and_rejects_duplicate_leakage(self):
        plan = machinery_plan()
        split = plan['split']
        self.assertFalse(set(split['development']) & set(split['holdout']))
        self.assertEqual(split, grouped_split(plan['rows']))
        rows = copy.deepcopy(plan['rows'])
        rows[-1]['x'] = rows[0]['x']
        with self.assertRaisesRegex(ValueError, 'duplicate feature vector crosses groups'):
            grouped_split(rows)
        self.assertEqual(plan['target'], 'synthetic_math_only')
        self.assertFalse(plan['promotable'])
        self.assertEqual(plan['empirical_personal_fit']['compatible_initial_role_fit_labels'], 0)

    def test_math_artifact_rejected_for_personal_fit_before_deserialization(self):
        import tempfile
        from pathlib import Path
        ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ARTIFACT_ROOT) as folder:
            p = Path(folder)
            (p / 'metadata.json').write_text(json.dumps(dict(target='synthetic_math_only', promotable=False)))
            with patch('joblib.load') as loader:
                with self.assertRaisesRegex(ValueError, 'target incompatible'):
                    load_machinery_candidate(p, 'ridge', expected_target='personal_role_fit',
                                              expected_feature_schema={})
                loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
