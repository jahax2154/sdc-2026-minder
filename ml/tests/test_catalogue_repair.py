"""G1A-R pending/activation invariants; all approval fixtures are temporary tests."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from minder_ml.intelligence import catalogue_repair as repair
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.inference import recommend_profile


class CatalogueRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for relative in (repair.BATCH, repair.FACTS,
                         repair.BASE + '/batch_decision.pending.json',
                         'ml/data/review/three_roles.pending.json',
                         'ml/configs/intelligence/measurement_sources.v1.json'):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.root_patch = patch.object(repair, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def decision(self):
        # Deliberately synthetic test evidence; never saved into the real repo.
        path = repair.BASE + '/batch_decision.pending.json'
        d = json.loads((self.root / path).read_text())
        d.update(status='approved', decision_id='SYNTHETIC-TEST-NOT-REAL-APPROVAL',
                 reviewer_id='synthetic-test-reviewer', decided_at='2026-10-21T00:00:00+00:00',
                 rationale='Unit test only; not an actual team decision',
                 accepted_effort_method_id='synthetic-test-estimate-method')
        batch = repair.load_batch()
        d['assessment_instance_ids'] = [r['instance_id'] for r in batch['assessment_instances']]
        for e in d['task_effort_estimates']:
            e.update(low=1, high=2, basis='Synthetic test-only estimate, not measured work or a sourced fact',
                     basis_kind='accepted_template_estimate', evidence_ids=['decision:' + d['decision_id']])
        (self.root / path).write_text(json.dumps(d))
        return path, d

    def test_pending_batch_validates_without_supplying_hours(self):
        b = repair.load_batch()
        self.assertFalse(b['active'])
        self.assertEqual(len(b['milestone_templates']), 3)
        self.assertEqual(sum(len(m['tasks']) for m in b['milestone_templates']), 6)
        self.assertTrue(all(t['effort'] is None for m in b['milestone_templates'] for t in m['tasks']))
        self.assertTrue(all(m['provenance_class'] == 'llm-proposed' for m in b['milestone_templates']))

    def test_pending_cannot_activate_or_write_registry(self):
        registry = self.root / 'ml/configs/intelligence/measurement_sources.v1.json'
        before = registry.read_bytes()
        with self.assertRaisesRegex(ValueError, 'not approved'):
            repair.activate_batch(decision_path=repair.BASE + '/batch_decision.pending.json')
        self.assertEqual(registry.read_bytes(), before)
        self.assertFalse((self.root / repair.BASE / 'accepted').exists())

    def test_decision_binds_exact_batch_hash(self):
        path, d = self.decision()
        d['batch_sha256'] = '0' * 64
        (self.root / path).write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'exact batch'):
            repair.activation_plan(decision_path=path)

    def test_unknown_zero_or_unrelated_effort_cannot_activate(self):
        path, d = self.decision()
        for update in ({'high': None}, {'low': 0, 'high': 0}, {'low': 5, 'high': 1},
                       {'unit': 'minutes'}, {'evidence_ids': ['unrelated-course-duration']},
                       {'basis_kind': 'inferred-from-skill-coverage'}):
            with self.subTest(update=update):
                broken = copy.deepcopy(d)
                broken['task_effort_estimates'][0].update(update)
                (self.root / path).write_text(json.dumps(broken))
                with self.assertRaises(ValueError): repair.activation_plan(decision_path=path)

    def test_assessment_instances_required_and_synthetic(self):
        path, d = self.decision()
        d['assessment_instance_ids'] = []
        (self.root / path).write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'exact proposed assessment'):
            repair.activation_plan(decision_path=path)
        batch_path = self.root / repair.BATCH
        batch = json.loads(batch_path.read_text())
        batch['assessment_instances'][0]['data_class'] = 'private'
        batch_path.write_text(json.dumps(batch))
        with self.assertRaisesRegex(ValueError, 'synthetic'):
            repair.load_batch()

    def test_activation_plan_is_read_only(self):
        path, d = self.decision()
        registry = self.root / 'ml/configs/intelligence/measurement_sources.v1.json'
        before = registry.read_bytes()
        plan = repair.activation_plan(decision_path=path)
        self.assertEqual(registry.read_bytes(), before)
        self.assertFalse((self.root / repair.BASE / 'accepted').exists())
        self.assertEqual(plan['source']['decision']['decision_id'], d['decision_id'])
        self.assertEqual(len(plan['source']['milestone_templates']), 3)

    def test_changed_source_dependency_rejected(self):
        facts = self.root / repair.FACTS
        facts.write_text(facts.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'dependency changed'):
            repair.load_batch()

    def test_essential_criteria_cannot_be_dropped(self):
        path = self.root / repair.BATCH
        b = json.loads(path.read_text())
        b['milestone_templates'][0]['criteria'].pop()
        path.write_text(json.dumps(b))
        with self.assertRaisesRegex(ValueError, 'essential draft criterion'):
            repair.load_batch()

    def test_future_activation_round_trip_is_temp_only_and_idempotent(self):
        path, _ = self.decision()
        reg = repair.activate_batch(decision_path=path)
        registry = self.root / 'ml/configs/intelligence/measurement_sources.v1.json'
        initial_bytes = registry.read_bytes()
        self.assertEqual(repair.activate_batch(decision_path=path), reg)
        self.assertEqual(registry.read_bytes(), initial_bytes)
        batch = repair.load_batch()
        roles = [{'role_id': m['role_id'], 'version': 'synthetic-test-only', 'milestone': None}
                 for m in batch['milestone_templates']]
        # Only the future release loader/source path is exercised against temp data.
        with patch.object(repair, 'repaired_catalogue', return_value=roles), \
             patch('minder_ml.intelligence.policy_sources.ROOT', self.root), \
             patch('minder_ml.intelligence.policy_features.ROOT', self.root):
            loaded = repair.load_catalogue(source_id=reg['source_id'])
            profile = {'profile_id': 'synthetic-test-future-activation', 'version': 'test-only',
                       'data_class': 'synthetic', 'hours_per_week': 0, 'planning_horizon': {'weeks': 12}}
            answers = {}
            for role in loaded:
                m = role['milestone']
                answers[role['role_id']] = {
                    'profile_version': profile['version'], 'milestone_version': m['version'],
                    'criterion_assessments': [{'criterion_id': c['criterion_id'],
                        'milestone_version': m['version'], 'anchor_version': c['anchor_version'],
                        'value': 1, 'basis': 'anchored_self_report', 'evidence_ids': ['synthetic-answer']}
                        for c in m['criteria']],
                    'interest_tags': [{'tag_id': t['tag_id'], 'value': 'interested', 'evidence_ids': ['synthetic-answer']} for t in m['interest_tags']],
                    'work_style_tags': [{'tag_id': t['tag_id'], 'value': 'compatible', 'evidence_ids': ['synthetic-answer']} for t in m['work_style_tags']],
                    'resources': [{'alternative_id': 'browser-and-local-written-workbook', 'value': 'accessible', 'evidence_ids': ['synthetic-answer']}]}
            result = recommend_profile(profile, loaded, answers_by_role=answers)
            self.assertEqual(len(result['recommendation']['options']), 3)
            self.assertTrue(all(o['personal_fit_index'] == 80 for o in result['recommendation']['options']))
            # These are synthetic future-activation tests, not real approved roles or output coverage.


class ActualReferenceRepairTests(unittest.TestCase):
    def test_taxonomy_and_defaults_are_scoped_not_milestone_approval(self):
        roles = repair.repaired_catalogue()
        self.assertEqual(len(roles), 3)
        self.assertTrue(all(r['identifier']['taxonomy_edition'] == '2019' for r in roles))
        self.assertTrue(all(r['identifier']['database_version'] == '31.0' for r in roles))
        self.assertTrue(all(r['milestone'] is None for r in roles))
        self.assertTrue(all(c['weight'] == 1 for r in roles for c in r['criterion_policy_defaults']))
        self.assertTrue(all(r['optional_crosswalk_status'].startswith('quarantined') for r in roles))
