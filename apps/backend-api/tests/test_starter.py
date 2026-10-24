"""Real pinned catalogue with normal intake only; no anchored evidence/model."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from support import AppCase
from minder_app.store import AppError
from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.app_context import CareerServices
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.personal_service import PersonalMatchingService


class StarterTests(AppCase):
    @classmethod
    def setUpClass(cls):
        catalogue = OccupationalCatalogue()
        roles = catalogue.roles()
        market = MarketEvidenceService(aliases={'role': {r['role_id']: r['role_id'].split(':', 1)[1] for r in roles}})
        cls.services = CareerServices(PersonalMatchingService(market), market, roles, list(catalogue.coverage['sources']))
        cls.services.role_reference = catalogue.reference

    def setUp(self):
        super().setUp()
        self.app.services = self.services

    def intake(self, **extra):
        metadata = dict(stage='studying', objective='fit', context='Computer science',
            interests=['software development'], self_reported_skills=['Python'],
            experience_state='none_yet', interests_uncertain=False, weekly_study_hours=6)
        metadata.update(extra)
        return self.app.dispatch('PUT', '/api/profile', {'profile': {'onboarding': metadata}}, self.token)

    def call(self, **body):
        return self.app.dispatch('POST', '/api/product/starter-recommendations', body, self.token)

    def test_normal_onboarding_gives_five_supported_personalised_starters_without_assessment(self):
        profile = self.intake()
        result = self.call()
        Draft202012Validator(json.loads((Path(__file__).resolve().parents[3] /
            'contracts/starter-recommendation.v1.schema.json').read_text())).validate(result)
        self.assertEqual(len(result['options']), 5)
        self.assertEqual(result['coverage']['supported_considered'], 910)
        self.assertTrue(any('Software' in o['label'] or 'Computer' in o['label'] for o in result['options']))
        self.assertTrue(all(o['matched_topics'] and o['sources'] and o['requirements']['skills'] for o in result['options']))
        self.assertTrue(all(o['personal_assessment'] is None and o['status'] == 'provisional' for o in result['options']))
        self.assertEqual(self.store.get(profile['profile_id'], 'profile', profile['profile_id']), profile)
        self.assertEqual(profile['evidence'], [])
        self.assertEqual([c['value'] for c in profile['constraints'] if c['scope'] == 'weekly_hours'], [6])
        self.assertEqual(self.store.list(profile['profile_id'], 'plan'), [])
        self.assertFalse(self.services.personal.input_readiness(profile)['global_minimum_possible'])

    def test_different_interests_and_field_change_shortlist(self):
        first = self.intake()
        computer = self.call()
        self.app.dispatch('PUT', '/api/profile', {'profile': {'onboarding': {
            'context': 'Nursing healthcare', 'interests': ['patient care nursing'], 'self_reported_skills': []}},
            'expected_version': first['version']}, self.token)
        health = self.call()
        self.assertNotEqual([o['role_id'] for o in computer['options']], [o['role_id'] for o in health['options']])
        self.assertTrue(any('Nurs' in o['label'] for o in health['options']))

    def test_uncertainty_and_explicit_none_are_not_universal_prerequisites(self):
        self.intake(context='Undecided', interests=[], self_reported_skills=[], interests_uncertain=True,
            weekly_study_hours=None)
        result = self.call()
        self.assertEqual(len(result['options']), 5)
        self.assertTrue(all(o['personal_assessment'] is None for o in result['options']))
        self.assertIsNone(result['planning_input']['weekly_study_hours'])

    def test_hard_restriction_and_preference_demotion_reset(self):
        profile = self.intake()
        first = self.call()
        rid = first['options'][0]['role_id']
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': {'preferences': [dict(
            entity_type='role', entity_id=rid, state='not_interested', authorizing_request_id='explicit-test')]},
            'expected_version': profile['version']}, self.token)
        negative = self.call()
        self.assertEqual(negative['coverage']['after_explicit_restrictions'], 910)
        self.assertNotIn(rid, [o['role_id'] for o in negative['options']])
        self.assertIn(rid, negative['deprioritized_role_ids'])
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': {'preferences': []},
            'expected_version': profile['version']}, self.token)
        self.assertEqual([o['role_id'] for o in self.call()['options']], [o['role_id'] for o in first['options']])
        self.app.dispatch('PUT', '/api/profile', {'profile': {'constraints': [dict(constraint_id='only-role',
            scope='role_allowlist', hard=True, value='["'+rid+'"]', unit='role_ids_json', evidence_id='explicit-test')]},
            'expected_version': profile['version']}, self.token)
        self.assertEqual([o['role_id'] for o in self.call()['options']], [rid])

    def test_invalid_limit_and_no_profile_fail_explicitly(self):
        for limit in [0, 6, True, '5']:
            with self.assertRaises(AppError):
                self.call(limit=limit)
        with self.assertRaises(AppError):
            self.call()

    def test_time_reset_is_pathway_only_and_unrelated_profile_edit_does_not_restore_old_capacity(self):
        profile = self.intake()
        constraints = copy.deepcopy(profile['constraints'])
        constraints[0]['value'] = 4
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': {'constraints': constraints},
            'expected_version': profile['version']}, self.token)
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': profile,
            'expected_version': profile['version']}, self.token)
        self.assertEqual(profile['constraints'][0]['value'], 4)
        self.assertEqual(self.call()['planning_input']['weekly_study_hours'], 4)
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': {'onboarding': {'weekly_study_hours': None}},
            'expected_version': profile['version']}, self.token)
        self.assertEqual(profile['constraints'], [])
        self.assertEqual(profile['evidence'], [])

    def test_missing_market_service_keeps_provisional_exploration_not_zero_demand(self):
        from unittest.mock import patch
        self.intake()
        with patch.object(self.services.personal, 'evidence_for', side_effect=OSError('source offline')):
            result = self.call()
        self.assertEqual(len(result['options']), 5)
        self.assertEqual(result['coverage']['returned_with_supported_market_comparison'], 0)
        self.assertTrue(all(o['market_evidence_status'] == 'unavailable' for o in result['options']))
