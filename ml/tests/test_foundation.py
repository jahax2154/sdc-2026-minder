"""Math/application checks only; never fit a learner on an unauthorized runner."""

import copy
import csv
from dataclasses import asdict
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from minder_ml.intelligence import recommend
from minder_ml.intelligence import artifacts
from minder_ml.intelligence.evaluation import (
    ANNOTATION_COLUMNS, read_annotations, split_groups, partition, diagnostics, counterfactuals)
from minder_ml.intelligence.features import build_features, skill_coverage, time_feasibility, feature_matrix
from minder_ml.intelligence.llm import DisabledExplanationAdapter
from minder_ml.intelligence.schemas import FEATURE_VERSION, RUBRIC_VERSION, FeatureSnapshot, RoleInput
from minder_ml.intelligence.scoring import baseline, combine, learned_score, validate_weights

ROOT = Path(__file__).resolve().parents[2]


def snap(values=(.6, .8, .5, 1, .7), q=1):
    return FeatureSnapshot(*values, assessed_requirement_fraction=q)


def service(roles=None, **kwargs):
    return recommend(roles if roles is not None else [RoleInput("role-A", snap(), [])],
                     profile_version="synthetic-v1", evidence_snapshot_id="synthetic-evidence-v1",
                     role_catalogue_version="synthetic-catalogue-v1", **kwargs)


def annotation(**kwargs):
    row = dict(zip(ANNOTATION_COLUMNS[:9], ["p1", "g1", "r1", "p-v1", "catalogue-v1",
                                          FEATURE_VERSION, RUBRIC_VERSION, "fixture-reviewer-not-human", "synthetic validator fixture only"]))
    row.update(profile_is_synthetic="true", reviewer_independent="true", preparation_horizon_weeks="12",
               annotation_status="reviewed", relevance_grade="1", **{k: str(v) for k, v in asdict(snap()).items()
                                                                      if k in ANNOTATION_COLUMNS and k not in ("feature_schema_version", "preparation_horizon_weeks")})
    row.update(kwargs)
    return row


class MathTests(unittest.TestCase):
    def test_baseline_golden_extremes_and_absolute_low_scores(self):
        self.assertAlmostEqual(baseline(snap()), 67)
        self.assertEqual(baseline(snap([0] * 5)), 0)
        self.assertEqual(baseline(snap([1] * 5)), 100)
        self.assertAlmostEqual(baseline(snap([.1] * 5)), 10)

    def test_baseline_monotonicity(self):
        for i in range(5):
            values = [.25] * 5
            before = baseline(snap(values))
            values[i] += .1
            self.assertGreaterEqual(baseline(snap(values)), before)

    def test_bad_weights_are_rejected_without_normalizing(self):
        for weights in ([1] * 5, [-.1, .4, .3, .2, .2], [math.nan] * 5,
                        [math.inf] * 5, [.5, .5], [.4, .2, .2, .1, .10001]):
            with self.assertRaises(ValueError):
                validate_weights(weights)

    def test_invalid_feature_values(self):
        for value in (-1, 1.01, math.inf, math.nan, True, "0.5"):
            with self.assertRaises(ValueError):
                snap([value, .5, .5, .5, .5])

    def test_unknown_skill_is_not_zero(self):
        self.assertEqual(skill_coverage([(2, None), (0, .5)]), (None, 0))
        self.assertEqual(skill_coverage([(1, 0), (1, None)]), (0, .5))
        self.assertEqual(skill_coverage([(1, .5), (3, 1)]), (.875, 1))

    def test_invalid_catalogue_is_not_user_inability(self):
        for catalogue in ([], [(0, None)], [(-1, .5)], [(1, 2)], [(math.inf, .5)]):
            with self.assertRaisesRegex(ValueError, "catalogue|weight|fraction"):
                skill_coverage(catalogue)

    def test_time_zero_unknown_and_range(self):
        self.assertEqual(time_feasibility(0, 30), 0)
        self.assertEqual(time_feasibility(None, 0), 1)
        self.assertIsNone(time_feasibility(None, 30))
        self.assertIsNone(time_feasibility(5, None))
        self.assertEqual(time_feasibility(1, 24, 12), .5)
        self.assertEqual(time_feasibility(100, 1), 1)
        for h, e, horizon in [(-1, 10, 12), (None, -1, 12), (1, 10, 0), (1, math.inf, 12), (math.nan, 0, 12)]:
            with self.assertRaises(ValueError):
                time_feasibility(h, e, horizon)

    def test_complete_evidence_policy(self):
        partial = build_features([(1, .5), (1, None)], .5, 1, .5, 2, 20)
        self.assertEqual(partial.assessed_requirement_fraction, .5)
        self.assertFalse(partial.eligible)
        with self.assertRaises(ValueError):
            baseline(partial)
        self.assertTrue(snap(q=1 - 1e-10).eligible)
        self.assertFalse(snap(q=.999).eligible)

    def test_effort_range_and_selected_estimate_are_preserved(self):
        snapshot = build_features([(1, .5)], .5, 1, .5, 2, 30, 12, 20, 40)
        self.assertEqual(snapshot.preparation_evidence.effort_hours_used, 30)
        self.assertEqual(snapshot.preparation_evidence.effort_low_hours, 20)
        self.assertEqual(snapshot.preparation_evidence.effort_high_hours, 40)
        self.assertAlmostEqual(snapshot.time_feasibility, .8)
        with self.assertRaises(ValueError):
            build_features([(1, .5)], .5, 1, .5, 2, 50, 12, 20, 40)

    def test_feature_allowlist_and_version(self):
        row = asdict(snap())
        row.update(relevance_grade=2, market_index=100, reviewer_id=999)
        self.assertEqual(feature_matrix([FeatureSnapshot.from_dict(row)]), [[.6, .8, .5, 1., .7]])
        row["feature_schema_version"] = "other"
        with self.assertRaises(ValueError):
            FeatureSnapshot.from_dict(row)

    def test_learned_mapping_and_combination(self):
        self.assertEqual([learned_score(x) for x in (-2, 0, 1, 2, 4)], [0, 0, 50, 100, 100])
        self.assertAlmostEqual(combine(67, 80), 70.9)
        for f, d, w in [(0, 0, 0), (100, 100, 1), (10, 90, .7), (90, 10, .5)]:
            self.assertTrue(0 <= combine(f, d, w) <= 100)
        for args in [(1, 101, .7), (1, 2, -1), (math.nan, 2, .7)]:
            with self.assertRaises(ValueError):
                combine(*args)


class ApplicationTests(unittest.TestCase):
    def test_default_versioned_result_and_stable_ties(self):
        result = service([RoleInput("B", snap(), []), RoleInput("A", snap(), [])])
        self.assertEqual(result.scorer_kind, "baseline")
        self.assertEqual(result.result_schema_version, "minder-recommendation-v1")
        self.assertEqual([r.role_id for r in result.options], ["A", "B"])
        self.assertAlmostEqual(result.options[0].personal_fit_index, 67)

    def test_missing_market_policy_entire_set(self):
        result = service()
        self.assertEqual(result.ranking_mode, "personal_fit_only")
        self.assertIsNone(result.options[0].market_assessment_index)
        self.assertIsNone(result.options[0].overall_match_index)

    def test_missing_information_visible(self):
        result = service([RoleInput("unknown", snap([None, .5, .5, .5, .5], q=0), [])])
        self.assertEqual(result.result_kind, "insufficient_information")
        self.assertEqual(result.options, [])
        self.assertIsNone(result.unscored_roles[0].feature_components["skill_coverage"])
        self.assertEqual(result.unscored_roles[0].evidence_coverage, 0)

    def test_unavailable_trained_selection_never_falls_back(self):
        for kind in ("ridge", "xgboost"):
            result = service(scorer_kind=kind)
            self.assertEqual(result.result_kind, "model_not_ready")
            self.assertEqual(result.scorer_kind, kind)
            self.assertEqual(result.options, [])
            self.assertIsNone(result.unscored_roles[0].personal_fit_index)

    def test_missing_artifact_is_explicit(self):
        result = service(scorer_kind="ridge", model_version="nonexistent-run")
        self.assertEqual(result.result_kind, "model_not_ready")

    def test_empty_comparison_set(self):
        self.assertEqual(service([]).result_kind, "insufficient_information")

    def test_disabled_llm_cannot_alter_numeric_result(self):
        result = service()
        original = copy.deepcopy(result.to_dict())
        explanation = DisabledExplanationAdapter().explain(result, [])
        self.assertEqual(explanation.status, "disabled")
        self.assertEqual(explanation.proposed_changes, [])
        self.assertEqual(result.to_dict(), original)

    def test_duplicate_roles_rejected(self):
        with self.assertRaises(ValueError):
            service([RoleInput("A", snap(), []), RoleInput("A", snap(), [])])

    def test_horizon_mismatch_requires_rebuilding_features(self):
        with self.assertRaisesRegex(ValueError, "horizon"):
            service(preparation_horizon_weeks=24)

    def test_artifact_traversal_and_synthetic_selection_rejected(self):
        with self.assertRaises(ValueError):
            artifacts.run_path("../outside")
        with tempfile.TemporaryDirectory() as temp, patch.object(artifacts, "ARTIFACT_ROOT", Path(temp)):
            path = Path(temp) / "smoke-test"
            path.mkdir()
            (path / "metadata.json").write_text(json.dumps({"evaluation_status": "synthetic_smoke_only"}))
            result = service(scorer_kind="ridge", model_version="smoke-test")
            self.assertEqual(result.result_kind, "model_not_ready")

    def test_incompatible_horizon_prevents_loading(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(artifacts, "ARTIFACT_ROOT", Path(temp)):
            path = Path(temp) / "reviewed-run"
            path.mkdir()
            meta = {"evaluation_status": "holdout_evaluated", "selected_candidate": "ridge",
                    "feature_names": list(snap().components()), "feature_schema_version": FEATURE_VERSION,
                    "rubric_version": RUBRIC_VERSION, "score_mapping_version": "grade-to-index-v1",
                    "ranking_policy_version": "personal-fit-role-id-v1", "compatibility": {
                        "preparation_horizon_weeks": 12, "role_catalogue_version": "synthetic-catalogue-v1"}}
            (path / "metadata.json").write_text(json.dumps(meta))
            role = RoleInput("A", FeatureSnapshot(.6, .8, .5, 1, .7, 1,
                                                  preparation_horizon_weeks=24), [])
            result = service([role], scorer_kind="ridge", model_version="reviewed-run", preparation_horizon_weeks=24)
            self.assertEqual(result.result_kind, "model_not_ready")

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn not installed")
    def test_unfitted_or_tampered_pipeline_is_not_ready(self):
        # Serialization of an UNFITTED pipeline only: no training evidence implied.
        from minder_ml.intelligence.estimators import make_estimator
        with tempfile.TemporaryDirectory() as temp, patch.object(artifacts, "ARTIFACT_ROOT", Path(temp)):
            run = artifacts.run_path("test-unfitted")
            run.mkdir()
            _, info = artifacts.save_candidate(run, "ridge", make_estimator("ridge"), {})
            meta = artifacts.metadata_base({}, {"preparation_horizon_weeks": 12,
                "role_catalogue_version": "synthetic-catalogue-v1"}, {}, {})
            meta.update(evaluation_status="holdout_evaluated", selected_candidate="ridge", candidates={"ridge": info})
            artifacts.write_json(run / "metadata.json", meta)
            self.assertEqual(service(scorer_kind="ridge", model_version="test-unfitted").result_kind, "model_not_ready")
            (run / "ridge/pipeline.joblib").write_bytes(b"tampered-test-file")
            self.assertEqual(service(scorer_kind="ridge", model_version="test-unfitted").result_kind, "model_not_ready")

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "optional jsonschema not installed")
    def test_results_match_executable_contract(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "contracts/recommendation-result.v1.schema.json").read_text())
        validator = Draft202012Validator(schema)
        for result in (service(), service([]), service(scorer_kind="ridge"),
                       service([RoleInput("P", snap([None, .5, .5, .5, .5], q=0), [])])):
            validator.validate(result.to_dict())


class EvaluationTests(unittest.TestCase):
    def read(self, rows):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "annotations.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=ANNOTATION_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            return read_annotations(path)

    def test_empty_template_is_not_evaluated(self):
        rows, report = self.read([])
        self.assertEqual(rows, [])
        self.assertEqual(report["eligible_reviewed_groups"], 0)
        self.assertEqual(report["empirical_status"], "not_evaluated")

    def test_pending_grades_remain_blank(self):
        rows, report = self.read([annotation(annotation_status="pending", relevance_grade="", reviewer_id="")])
        self.assertEqual(rows, [])
        self.assertEqual(report["pending_rows"], 1)
        self.assertEqual(report["errors"], [])

    def test_review_provenance_and_complete_features_required(self):
        for changes in ({"reviewer_id": ""}, {"review_reason": ""}, {"reviewer_independent": "false"},
                        {"relevance_grade": ""}, {"skill_coverage": ""},
                        {"assessed_requirement_fraction": ".5"}, {"profile_is_synthetic": "false"},
                        {"preparation_horizon_weeks": "nan"}, {"annotation_status": "pending"}):
            rows, report = self.read([annotation(**changes)])
            self.assertTrue(report["errors"], changes)
            self.assertEqual(rows, [])

    def test_duplicate_and_incompatible_rows_rejected(self):
        for rows in ([annotation(), annotation()],
                     [annotation(), annotation(role_id="r2", preparation_horizon_weeks="24")],
                     [annotation(), annotation(role_id="r2", profile_group_id="different")]):
            _, report = self.read(rows)
            self.assertTrue(report["errors"])

    def test_group_split_reproducible_and_no_leakage(self):
        rows = [{"profile_group_id": f"g{i}"} for i in range(25) for _ in range(8)]
        split = split_groups(rows)
        self.assertEqual(split, split_groups(rows))
        self.assertEqual(len(split["development"]), 20)
        self.assertEqual(len(split["holdout"]), 5)
        self.assertEqual(len(partition(rows, split, "development")), 160)
        with self.assertRaises(ValueError):
            split_groups(rows, {"development": ["g0"], "holdout": ["g0"]})

    def test_small_groups_are_exploratory(self):
        self.assertEqual(split_groups([{"profile_group_id": "g1"}])["holdout"], [])

    def test_linear_ndcg_with_stable_ties_and_clipped_mae(self):
        rows = [{"profile_id": "p", "role_id": role, "relevance_grade": grade}
                for role, grade in [("A", 0), ("B", 2), ("C", 1)]]
        result = diagnostics(rows, [1, 1, 1])
        expected = (2 / math.log2(3) + 1 / math.log2(4)) / (2 + 1 / math.log2(3))
        self.assertAlmostEqual(result["mean_ndcg_at_3"], expected)
        self.assertEqual(result["score_tie_pairs"], 3)
        self.assertAlmostEqual(diagnostics(rows, [-1, 3, 1])["mae_served_grade"], 0)
        self.assertAlmostEqual(diagnostics(rows, [-1, 3, 1])["clipping_rate"], 2 / 3)

    def test_all_weak_profiles_are_undefined_not_success(self):
        result = diagnostics([{"profile_id": "p", "role_id": "r", "relevance_grade": 0}], [0])
        self.assertIsNone(result["mean_ndcg_at_3"])
        self.assertEqual(result["idcg_zero_profiles"], ["p"])

    def test_bounded_baseline_counterfactuals(self):
        row = {"profile_id": "p", "role_id": "r", "snapshot": snap()}
        report = counterfactuals("baseline", None, [row])
        self.assertEqual(report["reversals"], [])
        self.assertEqual(report["perturbations"], 4)

    def test_training_requires_verified_runner(self):
        with self.assertRaisesRegex(ValueError, "runner_unavailable"):
            artifacts.require_runpod(None)

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn not installed")
    def test_frozen_selection_and_once_only_holdout_orchestration_without_fitting(self):
        # Pure control-flow test: fit/model/persistence are stubs, not learner evidence.
        from minder_ml.intelligence import training
        from minder_ml.intelligence.evaluation import predictions
        rows = [annotation(profile_id=f"p{i}", profile_group_id=f"g{i}", role_id=f"r{j}")
                for i in range(5) for j in range(3)]
        runner = {"execution_location": "test-stub-no-fitting"}
        with tempfile.TemporaryDirectory() as temp, patch.object(artifacts, "ARTIFACT_ROOT", Path(temp) / "artifacts"):
            path = Path(temp) / "synthetic-control-fixture.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=ANNOTATION_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            with patch.object(artifacts, "require_runpod", return_value=runner), \
                 patch.object(training, "make_estimator", return_value=object()), \
                 patch.object(artifacts, "fit_timed", return_value={}) as fit_stub, \
                 patch.object(training, "save_checked", return_value={"pipeline_sha256": "test-stub-no-model"}), \
                 patch.object(training, "counterfactuals", return_value={"test_stub": True}), \
                 patch.object(training, "predictions", side_effect=lambda kind, model, rr: predictions("baseline", None, rr)):
                result = training.compare(path, "test-control-run", "test-stub")
            self.assertEqual(result["selected_candidate"], "baseline")
            self.assertEqual(result["development_groups"], 4)
            self.assertEqual(result["holdout_groups"], 1)
            self.assertTrue(all(len(call.args[1]) <= 12 for call in fit_stub.call_args_list))
            run = artifacts.run_path("test-control-run")
            original = (run / "selection.json").read_text()
            original_metrics = (run / "metrics.json").read_text()
            (run / "selection.json").write_text(original + " ")
            with self.assertRaisesRegex(ValueError, "selection changed"):
                training.final_evaluate(path, "test-control-run")
            (run / "selection.json").write_text(original)
            final = training.final_evaluate(path, "test-control-run")
            self.assertEqual(final["status"], "holdout_evaluated")
            self.assertEqual(final["metrics"]["baseline"]["rows"], 3)
            with self.assertRaises(ValueError):
                training.final_evaluate(path, "test-control-run")
            # Simulate an accidental metadata rollback: the persistent once-only marker remains.
            meta = json.loads((run / "metadata.json").read_text())
            meta["evaluation_status"] = "development_only"
            (run / "metadata.json").write_text(json.dumps(meta))
            (run / "metrics.json").write_text(original_metrics)
            with self.assertRaises(FileExistsError):
                training.final_evaluate(path, "test-control-run")


if __name__ == "__main__":
    unittest.main()
