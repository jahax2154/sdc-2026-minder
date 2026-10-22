"""Initial occupational matching regressions; no empirical validity claims."""
import unittest
import copy
from unittest.mock import patch

from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.service_contracts import validate
from minder_ml.intelligence.personal_service import PersonalMatchingService
from minder_ml.intelligence.personal_cli import synthetic_profile


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
        self.assertEqual(role['industry_mappings'], [])
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


if __name__ == '__main__':
    unittest.main()
