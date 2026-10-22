"""Initial occupational matching regressions; no empirical validity claims."""
import unittest

from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.service_contracts import validate


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


if __name__ == '__main__':
    unittest.main()
