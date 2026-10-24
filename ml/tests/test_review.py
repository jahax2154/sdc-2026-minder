"""Synthetic unit/control fixtures only. No actual reviewer or learner fitting."""

import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from minder_ml.intelligence import artifacts
from minder_ml.intelligence.features import criterion_gaps
from minder_ml.intelligence.review import prepare_profile
from minder_ml.intelligence.training import evaluate_baseline
from minder_ml.intelligence.evaluation import ANNOTATION_COLUMNS
from test_foundation import annotation

ROOT = Path(__file__).resolve().parents[2]


def fixture_review(**extra):
    return dict(review_status="reviewed", reviewer_id="unit-test-stub-not-human",
                review_reason="synthetic branch test, not review evidence", reviewed_at="test-only", **extra)


def fixture_inputs():
    roles = []
    profile = dict(profile_id="test-profile", profile_group_id="test-group", profile_version="test-v1",
                   profile_is_synthetic=True, preparation_horizon_weeks=12, hours_per_week=2,
                   criterion_assessments=[], role_assessments=[])
    for rid, c, i, effort, w in [("test-A", .6, .8, 48, .7), ("test-B", .2, .5, 12, .5), ("test-C", .8, .8, 48, .7)]:
        roles.append(fixture_review(role_id=rid, mapping_reviewed=True, evidence_ids=[],
            criteria=[fixture_review(criterion_id=cid, requirement_weight=1) for cid in ("criterion-1", "criterion-2")],
            feature_rubrics={n: fixture_review() for n in ("interest_alignment", "resource_feasibility", "work_style_alignment")},
            effort_estimate=fixture_review(effort_hours_used=effort)))
        for cid in ("criterion-1", "criterion-2"):
            if (rid, cid) != ("test-C", "criterion-2"):
                profile["criterion_assessments"].append(fixture_review(
                    role_id=rid, criterion_id=cid, demonstrated_fraction=c, evidence_ids=["test-assessment"]))
        profile["role_assessments"].append(fixture_review(role_id=rid,
            interest_alignment=i, resource_feasibility=1, work_style_alignment=w, evidence_ids=["test-review"]))
    return profile, dict(catalogue_version="test-catalogue", evidence_snapshot_id="test-evidence", roles=roles)


class ReviewTests(unittest.TestCase):
    def test_raw_builder_service_ordering_and_unknown_gaps(self):
        profile, catalogue = fixture_inputs()
        result = prepare_profile(profile, catalogue)
        options = result["recommendation"]["options"]
        self.assertEqual([r["role_id"] for r in options], ["test-A", "test-B"])
        self.assertAlmostEqual(options[0]["personal_fit_index"], 67)
        self.assertAlmostEqual(options[1]["personal_fit_index"], 53)
        unknown = result["recommendation"]["unscored_roles"][0]
        self.assertEqual(unknown["role_id"], "test-C")
        self.assertEqual(unknown["evidence_coverage"], .5)
        gaps = result["roles"][2]["criterion_gaps"]
        self.assertIsNone(gaps[1]["remaining_fraction"])
        self.assertEqual(gaps[1]["assessment_state"], "unknown")

    def test_pending_catalogue_never_reaches_feature_builder(self):
        profile, _ = fixture_inputs()
        catalogue = json.loads((ROOT / "ml/data/review/three_roles.pending.json").read_text())
        with patch("minder_ml.intelligence.review.build_features") as builder:
            result = prepare_profile(profile, catalogue)
        builder.assert_not_called()
        self.assertEqual(len(result["blocked_roles"]), 3)
        for role in result["roles"]:
            self.assertIsNone(role["evidence_coverage"])
            self.assertIsNone(role["feature_components"])
        self.assertEqual(result["recommendation"]["options"], [])

    def test_unknown_assessment_does_not_turn_into_zero(self):
        profile, catalogue = fixture_inputs()
        profile["criterion_assessments"][0]["review_status"] = "pending"
        result = prepare_profile(profile, catalogue)
        self.assertEqual(result["roles"][0]["feature_snapshot"]["assessed_requirement_fraction"], .5)
        self.assertIsNone(result["roles"][0]["criterion_gaps"][0]["remaining_fraction"])

    def test_missing_raw_profile_is_explicit(self):
        profile = json.loads((ROOT / "ml/data/review/profile_intake.pending.json").read_text())
        catalogue = json.loads((ROOT / "ml/data/review/three_roles.pending.json").read_text())
        with self.assertRaisesRegex(ValueError, "profile_id"):
            prepare_profile(profile, catalogue)

    def test_gap_math_and_duplicate_validation(self):
        rows = [dict(criterion_id="a", requirement_weight=1, demonstrated_fraction=.5),
                dict(criterion_id="b", requirement_weight=3, demonstrated_fraction=1)]
        self.assertAlmostEqual(sum(r["weighted_remaining_fraction"] for r in criterion_gaps(rows)), .125)
        with self.assertRaises(ValueError):
            criterion_gaps([rows[0], rows[0]])
        with self.assertRaises(ValueError):
            criterion_gaps([])

    def test_real_review_materials_have_no_generated_grades_or_approvals(self):
        path = ROOT / "ml/data/review"
        for name in ("three_roles.pending.json", "source_mappings.pending.json"):
            value = json.loads((path / name).read_text())
            def walk(obj):
                if isinstance(obj, dict):
                    if "review_status" in obj:
                        self.assertEqual(obj["review_status"], "pending")
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)
            walk(value)
        blind = json.loads((path / "blind_grading_packet.pending.json").read_text())
        for row in blind["role_cards"]:
            self.assertIsNone(row["relevance_grade"])
            self.assertIsNone(row["reviewer_id"])
        for forbidden in ("personal_fit_index", "overall_match_index", "baseline_score", "served_role_order"):
            self.assertNotIn(forbidden, (path / "blind_grading_packet.pending.json").read_text())

    @unittest.skipUnless((ROOT / "ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv").exists(), "source pack absent")
    def test_source_rows_match_each_proposed_role_and_skill(self):
        with (ROOT / "ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv").open(newline="") as stream:
            source = list(csv.DictReader(stream))
        catalogue = json.loads((ROOT / "ml/data/review/three_roles.pending.json").read_text())
        for role in catalogue["roles"]:
            for criterion in role["criteria"]:
                self.assertEqual(len(criterion["source_rows"]), 2)
                for ref in criterion["source_rows"]:
                    row = source[ref["row_1_based"] - 2]
                    self.assertEqual(row["O*NET-SOC Code"], role["role_id"])
                    self.assertEqual(row["Element Name"], criterion["source_skill_name"])
                    self.assertEqual(row["Scale ID"], ref["scale_id"])
                    self.assertEqual(row["Data Value"], ref["source_value"])

    def test_baseline_evaluation_needs_no_runner_and_keeps_holdout_closed(self):
        # Fictional annotation() records exercise control flow, not independent labels.
        rows = [annotation(profile_id=f"test-p{i}", profile_group_id=f"test-g{i}", role_id=f"test-r{j}")
                for i in range(5) for j in range(2)]
        with tempfile.TemporaryDirectory() as temp, patch.object(artifacts, "ARTIFACT_ROOT", Path(temp) / "artifacts"), \
             patch.object(artifacts, "fit_timed", side_effect=AssertionError("must not fit")):
            data = Path(temp) / "test-only.csv"
            def write(values):
                with data.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=ANNOTATION_COLUMNS)
                    writer.writeheader()
                    writer.writerows(values)
            write(rows)
            first = evaluate_baseline(data, "test-baseline-one")
            self.assertEqual(first["status"], "development_baseline_only")
            self.assertEqual(first["metrics"]["rows"], 8)
            changed = copy.deepcopy(rows)
            for row in changed:
                if row["profile_group_id"] in first["split"]["holdout"]:
                    row["relevance_grade"] = "2"
            write(changed)
            second = evaluate_baseline(data, "test-baseline-two")
            self.assertEqual(first["metrics"], second["metrics"])
            self.assertFalse((Path(temp) / "artifacts/test-baseline-one/heldout_predictions.csv").exists())


if __name__ == "__main__":
    unittest.main()
