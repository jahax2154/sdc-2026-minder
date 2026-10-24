"""Functional-gate API regressions over the actual pinned occupational sources."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from unittest.mock import patch
from support import AppCase
from minder_app.store import AppError
from minder_ml.intelligence.app_context import CareerServices
from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.personal_service import PersonalMatchingService

ROLE = 'onet:15-1252.00'


class RoleDisplayTests(AppCase):
    @classmethod
    def setUpClass(cls):
        catalogue = OccupationalCatalogue()
        roles = catalogue.roles()
        aliases = {r['role_id']: catalogue.reference(r['role_id'])['occupation']['O*NET-SOC Code'] for r in roles}
        market = MarketEvidenceService(aliases={'role': aliases})
        cls.services = CareerServices(PersonalMatchingService(market), market, roles,
            list(catalogue.coverage['sources']), mode='local_source_services')

    def setUp(self):
        super().setUp()
        self.app.services = self.services
        stamp = patch.object(self.services.personal, 'as_of', '2026-10-24T12:00:00+00:00')
        stamp.start()
        self.addCleanup(stamp.stop)

    def call(self, path='role-requirements', body=None, token=None):
        return self.app.dispatch('POST', '/api/' + path, body or {}, token or self.token)

    def select(self):
        self.app.dispatch('PUT', '/api/profile', {'profile': {'career_context': {'goals': 'Fictional test exploration'}}}, self.token)
        return self.app.dispatch('PUT', '/api/product/direction', dict(role_id=ROLE,
            expected_version=None, idempotency_key='choose'), self.token)

    def test_labels_distinct_source_measures_and_no_inferred_user_competence(self):
        original = copy.deepcopy(next(r for r in self.services.roles if r['role_id'] == ROLE))
        result = self.call(body={'role_id': ROLE})
        display = result['display']
        schema = json.loads((Path(__file__).resolve().parents[3] / 'contracts/role-display.v1.schema.json').read_text())
        Draft202012Validator(schema).validate(display)
        self.assertEqual(display['source_record_count'], 19)
        self.assertEqual(display['skill_count'], 10)
        skill = next(s for s in display['skills'] if s['subject_id'] == 'onet:element:2.A.1.a')
        self.assertEqual(skill['label'], 'Reading Comprehension')
        self.assertEqual(skill['label_source'], self.services.personal.ref['sources']['anchors'])
        self.assertEqual([(m['unit'], m['value']) for m in skill['measurements']], [('onet:IM', 3.5), ('onet:LV', 4.25)])
        for row, measurement in zip(original['requirements'], [m for s in display['skills'] for m in s['measurements']]):
            self.assertEqual(measurement['evidence_id'], row['evidence_id'])
            self.assertEqual(measurement['source'], row['provenance'])
        self.assertTrue(all(s['personal_evidence']['status'] == 'not_assessed' for s in display['skills']))
        self.assertEqual(result['role'], original)
        self.assertEqual(next(r for r in self.services.roles if r['role_id'] == ROLE), original)

    def test_every_current_requirement_has_a_sourced_label(self):
        identifiers = {e['subject_id'] for r in self.services.roles for e in r['requirements']}
        self.assertEqual(len(identifiers), 10)
        self.assertFalse(identifiers - set(self.services.personal.ref['skill_rubrics']))

    def test_omitted_id_resolves_saved_direction_without_mutation_or_cross_owner_leak(self):
        direction = self.select()
        result = self.call()
        self.assertEqual(result['role_selection'], dict(role_id=ROLE, source='saved_direction'))
        self.assertEqual(self.call('role-evidence')['role_selection'], result['role_selection'])
        self.assertEqual(self.app.dispatch('GET', '/api/product/direction', {}, self.token)['direction'], direction)
        with self.assertRaises(AppError) as error:
            self.call(token=self.store.session()['token'])
        self.assertEqual(error.exception.status, 422)

    def test_explicit_invalid_id_never_silently_uses_saved_direction(self):
        self.select()
        for identifier in [None, '', 'unknown-role', 42]:
            with self.assertRaises(AppError):
                self.call(body={'role_id': identifier})

    def test_optional_notes_and_anchored_conflicts_are_not_competence(self):
        ref = self.services.personal.ref
        row = copy.deepcopy(next(r for r in self.services.roles if r['role_id'] == ROLE)['requirements'][0])
        row.update(evidence_id='user-reading', unit='onet:LV', method_id='minder-anchored-evidence-v1', value=2)
        row['provenance']['evidence_type'] = 'explicit-user'
        row['assessment'] = dict(kind='self_report', rubric_version='onet31-essential-anchors-v1',
            statement='Fictional acceptance self-report of reading instructions.')
        profile = self.app.dispatch('PUT', '/api/profile', {'profile': {'evidence': [row]}}, self.token)
        def first():
            return self.call(body={'role_id': ROLE})['display']['skills'][0]['personal_evidence']
        self.assertEqual(first()['status'], 'anchored_evidence_recorded')
        conflicting = copy.deepcopy(row)
        conflicting.update(evidence_id='user-reading-conflict', value=4)
        self.app.dispatch('PUT', '/api/profile', {'profile': {'evidence': [row, conflicting]},
            'expected_version': profile['version']}, self.token)
        self.assertEqual(first()['status'], 'needs_clarification')
        self.assertNotIn('score', first())

    def test_forecast_unavailable_is_typed_and_independent_of_current_evidence(self):
        result = self.call('role-evidence', {'role_id': ROLE})
        self.assertIsNone(result['forecast_error'])
        self.assertEqual(result['forecast']['status'], 'unavailable')
        self.assertIsNone(result['forecast']['value'])
        self.assertTrue(result['forecast']['target_period'])
        self.assertTrue(any(r['status'] == 'available' for r in result['records']))
        for failure in [RuntimeError('private error detail'), {'invalid': 'forecast'}]:
            kwargs = {'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure}
            with patch.object(self.services.market, 'forecast', **kwargs):
                failed = self.call('role-evidence', {'role_id': ROLE})
            self.assertEqual(failed['records'], result['records'])
            self.assertIsNone(failed['forecast'])
            self.assertEqual(failed['forecast_error'], 'forecast_read_failed')
            self.assertNotIn('private error detail', str(failed))
