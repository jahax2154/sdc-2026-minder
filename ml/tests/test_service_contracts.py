"""G0 synthetic integration inputs; no empirical labels or paid execution."""
import copy
import json
from pathlib import Path
import unittest

from minder_ml.intelligence.service_contracts import (
    validate, next_calendar_quarter, public_recommendation,
    legacy_preparation_recommendation)
from minder_ml.intelligence.schemas import FeatureSnapshot, RoleInput
from minder_ml.intelligence.inference import recommend

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'contracts/fixtures/parallel-v1'


def fixture(name):
    return json.loads((FIXTURES / (name + '.json')).read_text())['payload']


class ContractTests(unittest.TestCase):
    def test_all_fixtures_validate_and_are_explicitly_synthetic(self):
        for path in sorted(FIXTURES.glob('*.json')):
            item = json.loads(path.read_text())
            with self.subTest(path=path.name):
                self.assertTrue(item['synthetic'])
                self.assertFalse(item['empirical_evidence'])
                validate(item['kind'], item['payload'])

    def test_unknown_is_not_zero(self):
        p = fixture('partial_profile')
        p['evidence'][0]['value'] = 0
        with self.assertRaises(ValueError):
            validate('Profile', p)
        p['evidence'][0]['state'] = 'known'
        validate('Profile', p)

    def test_preference_is_scoped_state(self):
        p = fixture('complete_profile')
        p['preferences'].append(copy.deepcopy(p['preferences'][0]))
        p['preferences'][1]['state'] = 'interested'
        with self.assertRaises(ValueError):
            validate('Profile', p)

    def test_next_quarter_year_and_leap_boundaries(self):
        self.assertEqual(next_calendar_quarter('2026-10-23T00:00:00Z'),
                         {'start': '2027-01-01', 'end': '2027-03-31'})
        self.assertEqual(next_calendar_quarter('2023-12-31T00:00:00Z'),
                         {'start': '2024-01-01', 'end': '2024-03-31'})
        self.assertEqual(next_calendar_quarter('2026-03-31T00:00:00Z')['start'], '2026-04-01')

    def test_unavailable_forecast_cannot_be_zero_or_wrong_quarter(self):
        m = fixture('forecast_unavailable')
        m['value'] = 0
        with self.assertRaises(ValueError):
            validate('MarketResult', m)
        m['value'] = None
        m['target_period']['start'] = '2026-10-01'
        with self.assertRaises(ValueError):
            validate('MarketResult', m)

    def test_pending_policy_cannot_score(self):
        p = fixture('complete_evidence_pending_policy')
        p.update(score_status='scored', score=80)
        with self.assertRaises(ValueError):
            validate('PersonalAssessment', p)

    def test_internal_market_fields_cannot_leak(self):
        r = fixture('recommendation_pending')
        public = public_recommendation(r)
        self.assertNotIn('internal', public)
        self.assertNotIn('internal_index', json.dumps(public))
        r['public']['internal_index'] = 80
        with self.assertRaises(Exception):
            public_recommendation(r)

    def test_pending_blend_rejected(self):
        r = fixture('recommendation_pending')
        r['internal']['combined_scores'] = [{'role_id': 'synthetic-role', 'score': 80}]
        with self.assertRaises(ValueError):
            validate('Recommendation', r)

    def test_proactive_write_needs_exact_approval(self):
        a = fixture('approval_required')
        a.update(execution_status='applied', resulting_state_version='v2')
        with self.assertRaises(ValueError):
            validate('Action', a)
        a.update(approval_state='approved', approved_proposal_id='wrong-proposal')
        with self.assertRaises(ValueError):
            validate('Action', a)
        a['approved_proposal_id'] = a['proposal_id']
        validate('Action', a)

    def test_direct_request_does_not_need_redundant_approval(self):
        a = fixture('direct_action')
        a.update(execution_status='applied', resulting_state_version='v2')
        validate('Action', a)
        a['authorizing_request_id'] = None
        with self.assertRaises(ValueError):
            validate('Action', a)

    def test_company_found_requires_official_evidence(self):
        c = fixture('no_company_role_found')
        c.update(status='found', role_id='synthetic-role')
        with self.assertRaises(ValueError):
            validate('CompanyRoleResult', c)

    def test_existing_legacy_service_and_golden_unchanged(self):
        result = recommend([RoleInput('synthetic-role', FeatureSnapshot(
            .6, .8, .5, 1, .7, assessed_requirement_fraction=1), [])],
            profile_version='synthetic-v1', evidence_snapshot_id='synthetic-v1',
            role_catalogue_version='synthetic-v1', scorer_kind='baseline')
        self.assertAlmostEqual(result.options[0].personal_fit_index, 67)
        self.assertTrue(callable(legacy_preparation_recommendation))

class UniquenessParityTests(unittest.TestCase):
    def test_optimized_unique_items_preserves_json_equality(self):
        import random
        from jsonschema import Draft202012Validator
        from minder_ml.intelligence.service_contracts import _DTOValidator
        old = Draft202012Validator({'uniqueItems': True})
        new = _DTOValidator({'uniqueItems': True})
        values=[None,False,True,0,1,1.0,0.0,'1','',[],{},[1],{'a':1},{'a':True},
                {'b':2,'a':1},{'a':1.0,'b':2}]
        arrays=[[a,b] for a in values for b in values]
        randomizer=random.Random(11)
        arrays += [randomizer.choices(values,k=randomizer.randint(0,30)) for _ in range(1000)]
        for value in arrays:
            self.assertEqual(old.is_valid(value),new.is_valid(value),value)

