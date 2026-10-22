"""Phase 2 engineering gates; fictional human flags exist only in temporary unit fixtures."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from minder_ml.intelligence.annotation_io import export_annotations, import_annotations
from minder_ml.intelligence.data_adapters import derive_profile
from minder_ml.intelligence.data_cli import validate_snapshot
from minder_ml.intelligence.data_pipeline import ROOT, PACK, parse_dosm, prepare_snapshot, sha
from minder_ml.intelligence.data_schemas import validate_entity
from minder_ml.intelligence.evaluation import read_annotations
from minder_ml.intelligence.market import compare_observations, observed_yoy, observed_share, build_market_views

PROFILE = ROOT / "ml/tests/fixtures/phase2_profile.synthetic.json"
ROLES = ROOT / "ml/data/review/phase2/roles.pending.json"


def approved_fixture():
    """NOT human review: synthetic approval branches for software tests only."""
    profile, roles = json.loads(PROFILE.read_text()), json.loads(ROLES.read_text())
    review = {"status": "approved", "reviewer_id": "unit-test-not-a-human", "rationale": "fictional unit fixture only", "reviewed_at": "2026-10-21T00:00:00Z"}
    for role in roles:
        role["preparation_milestone"] = "Fictional smoke milestone, not an approved career requirement"
        role["review"] = dict(review)
        for item in role["criteria"]:
            item["review"], item["requirement_weight"] = dict(review), 1
            profile["skill_observations"].append({"skill_id": item["skill_id"], "criterion_id": item["criterion_id"],
                "role_id": role["role_id"], "state": "demonstrated", "demonstrated_fraction": .5,
                "evidence_ids": ["synthetic-unit-evidence"], "review": dict(review)})
        for mapping in role["occupation_identifiers"]:
            mapping["review"] = dict(review)
        for rubric in role["feature_rubrics"].values():
            rubric["evidence_rule"], rubric["review"] = "fictional test input", dict(review)
        role["remaining_effort"].update(hours_used=0, basis="fictional unit value", review=dict(review))
        profile["role_alignments"].append({"role_id": role["role_id"], "interest_alignment": .5,
            "resource_feasibility": 1, "work_style_alignment": .5, "evidence_ids": ["synthetic-unit-alignment"], "review": dict(review)})
    return profile, roles


class CanonicalContractTests(unittest.TestCase):
    def test_pending_roles_and_unknown_profile_fields_are_valid_not_approved(self):
        profile, roles = json.loads(PROFILE.read_text()), json.loads(ROLES.read_text())
        validate_entity(profile)
        for role in roles:
            validate_entity(role)
            self.assertEqual(role["review"]["status"], "pending")
        self.assertIsNone(profile["education_experience"]["education"])

    def test_all_six_entity_enums_and_crosswalks(self):
        profile = json.loads(PROFILE.read_text())
        for path in ["role_market_crosswalks.pending.json", "skill_taxonomy_crosswalks.pending.json"]:
            for row in json.loads((ROLES.parent / path).read_text()):
                validate_entity(row)
        skill_mapping = json.loads((ROLES.parent / "role_market_crosswalks.pending.json").read_text())[0]
        skill_mapping["entity_type"] = "SkillTaxonomyCrosswalk"
        skill_mapping["mapping_id"] = "synthetic-schema-test-not-a-real-mapping"
        validate_entity(skill_mapping)
        for field, value in [("data_class", "public_real_person"), ("hours_per_week", -1), ("hours_per_week", float("nan"))]:
            bad = copy.deepcopy(profile)
            bad[field] = value
            with self.assertRaises(ValueError):
                validate_entity(bad)

    def test_approval_cannot_be_asserted_without_reviewed_content(self):
        role = json.loads(ROLES.read_text())[0]
        role["review"]["status"] = "approved"
        with self.assertRaises(ValueError):
            validate_entity(role)

    def test_weak_proposal_and_role_acceptance_are_not_gold(self):
        profile, roles = approved_fixture()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            export_annotations([profile], roles, folder / "packet")
            rows = json.loads((folder / "packet/responses.template.json").read_text())
            rows[0].update(grade=1, label_source="weak_auto_proposal")
            response = folder / "weak.json"
            response.write_text(json.dumps(rows))
            report = import_annotations(folder / "packet", response, folder / "import")
            self.assertEqual(report["weak_proposals"], 1)
            self.assertEqual(report["gold_labels"], 0)
            self.assertEqual(read_annotations(folder / "import/foundation_annotations.csv")[1]["rows"], 0)
            rows[0]["label_source"] = "role_accepted"
            with self.assertRaises(ValueError):
                validate_entity(rows[0])

    def test_private_profile_refused_before_writing_artifacts(self):
        profile = json.loads(PROFILE.read_text())
        profile["data_class"] = "private"
        validate_entity(profile)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "never-created"
            with self.assertRaises(ValueError):
                export_annotations([profile], json.loads(ROLES.read_text()), path)
            self.assertFalse(path.exists())


class BlindReviewTests(unittest.TestCase):
    def test_public_packet_edits_require_a_new_export(self):
        profile, roles = json.loads(PROFILE.read_text()), json.loads(ROLES.read_text())
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            export_annotations([profile], roles, folder / "packet")
            path = folder / "packet/packet.json"
            packet = json.loads(path.read_text())
            packet["pairs"][0]["role_requirements"]["title"] = "tampered unit test title"
            path.write_text(json.dumps(packet))
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                import_annotations(folder / "packet", folder / "packet/responses.template.json", folder / "import")

    def test_pending_round_trip_is_blind_and_preserves_missing_grades(self):
        profile, roles = json.loads(PROFILE.read_text()), json.loads(ROLES.read_text())
        with tempfile.TemporaryDirectory() as temp, patch("minder_ml.intelligence.review.recommend", side_effect=AssertionError("must not score")):
            folder = Path(temp)
            exported = export_annotations([profile], roles, folder / "packet")
            packet = (folder / "packet/packet.json").read_text()
            for forbidden in ("personal_fit_index", "overall_match_index", "baseline_score", "role_alignments", "feature_snapshot"):
                self.assertNotIn(forbidden, packet)
            imported = import_annotations(folder / "packet", folder / "packet/responses.template.json", folder / "import")
            self.assertEqual(exported["pairs"], 3)
            self.assertEqual(imported["gold_labels"], 0)
            self.assertEqual(imported["pending_rows"], 3)
            self.assertEqual(len(imported["unresolved_cases"]), 3)
            self.assertTrue(all(r["grade"] is None for r in json.loads((folder / "import/responses.json").read_text())))

    def test_independent_agreement_disagreement_and_context_rejection(self):
        profile, roles = approved_fixture()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            export_annotations([profile], roles, folder / "packet")
            responses = json.loads((folder / "packet/responses.template.json").read_text())
            responses[0].update(grade=1, label_source="human_reviewed", independent_review=True,
                reviewer_id="unit-test-not-human-A", rationale="fictional branch test", review_status="approved", reviewed_at="2026-10-21T00:00:00Z")
            response = folder / "responses.json"
            response.write_text(json.dumps(responses))
            result = import_annotations(folder / "packet", response, folder / "agree")
            self.assertEqual(result["gold_labels"], 1)
            eligible, _ = read_annotations(folder / "agree/foundation_annotations.csv")
            self.assertEqual(eligible[0]["profile_group_id"], profile["profile_family_id"])
            second = copy.deepcopy(responses[0])
            second.update(annotation_id="unit-test-second-judgment", reviewer_id="unit-test-not-human-B", grade=2)
            responses.append(second)
            response.write_text(json.dumps(responses))
            result = import_annotations(folder / "packet", response, folder / "disagree")
            self.assertEqual(result["gold_labels"], 0)
            self.assertEqual(len(result["disagreements"]), 1)
            responses[0]["profile_family_id"] = "tampered-family"
            response.write_text(json.dumps(responses))
            with self.assertRaises(ValueError):
                import_annotations(folder / "packet", response, folder / "bad")

    def test_canonical_adapter_keeps_service_contract_and_unknown_assessments(self):
        from jsonschema import Draft202012Validator
        profile, roles = approved_fixture()
        # Self-reported evidence is not an assessed criterion; one requirement becomes unknown.
        profile["skill_observations"][0]["state"] = "self_reported"
        result = derive_profile(profile, roles, include_scores=True)
        Draft202012Validator(json.loads((ROOT / "contracts/recommendation-result.v1.schema.json").read_text())).validate(result["recommendation"])
        unscored = result["recommendation"]["unscored_roles"]
        self.assertEqual(len(unscored), 1)
        self.assertEqual(unscored[0]["reason"], "insufficient_information")
        sidecar = next(r for r in result["roles"] if r["role_id"] == roles[0]["role_id"])
        self.assertIsNone(sidecar["criterion_gaps"][0]["remaining_fraction"])
        self.assertIn("source_ids", sidecar["criterion_gaps"][0])


@unittest.skipUnless((PACK / "sources_manifest.json").exists(), "DOSM source pack absent: P2-1 BLOCKED")
class SourceAndComparabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.quality, cls.provenance = parse_dosm()

    def observation(self, label="Managers", period="2026-04-01", dimension="occupation"):
        return copy.deepcopy(next(r for r in self.rows if r["period_start"] == period and r["dimension_scope"] == dimension and (r["occupation_label"] or r["industry_label"]) == label))

    def test_real_source_counts_and_round_trip(self):
        self.assertEqual(self.quality["validated_rows"], 952)
        self.assertEqual(self.quality["observed_numeric_rows"], 921)
        self.assertEqual(self.quality["missing_rows"], 31)
        self.assertEqual(self.quality["source_cell_round_trip_rows"], 952)
        self.assertEqual(self.quality["rejected_rows"], 0)
        self.assertEqual(len({r["observation_id"] for r in self.rows}), 952)

    def test_permitted_yoy_and_source_share(self):
        current, prior = self.observation(), self.observation(period="2025-04-01")
        yoy = observed_yoy(current, prior)
        self.assertTrue(yoy["comparable"])
        self.assertAlmostEqual(yoy["value"], 100 * (current["value"] / prior["value"] - 1))
        total = self.observation(label="Jumlah")
        share = observed_share(current, total)
        self.assertTrue(share["comparable"])
        self.assertAlmostEqual(share["value"], current["value"] / total["value"])
        self.assertEqual(share["denominator_observation_id"], total["observation_id"])

    def test_annual_country_provider_and_marginal_mismatch_rejected(self):
        a = self.observation()
        annual = self.observation(period="2025-04-01")
        annual.update(frequency="annual", period_start="2025-01-01", period_end="2025-12-31")
        self.assertFalse(compare_observations(a, annual)["comparable"])
        country = copy.deepcopy(a)
        country.update(geography_code="USA", source_coverage="different online provider", source_id="other-provider")
        self.assertIn("different_provider_counts_are_not_national_market_sizes", compare_observations(a, country, "cohort")["reasons"])
        industry = self.observation(label="Manufacturing", dimension="industry")
        self.assertIn("dimension_scope_mismatch", compare_observations(a, industry, "share")["reasons"])

    def test_missing_zero_taxonomy_and_methodology_preserved(self):
        a, b = self.observation(), self.observation(period="2025-04-01")
        b["value"] = 0
        self.assertIsNone(observed_yoy(a, b)["value"])
        b.update(value=None, data_quality_status="missing")
        self.assertIn("missing_observation", observed_yoy(a, b)["reasons"])
        b = self.observation(period="2025-04-01")
        b["taxonomy_version"] = "incompatible"
        self.assertFalse(compare_observations(a, b)["comparable"])
        a, b = self.observation(label="Unclassified", dimension="industry"), self.observation(label="Unclassified", period="2025-04-01", dimension="industry")
        self.assertIn("classification_continuity_requires_review", observed_yoy(a, b)["reasons"])

    def test_unsupported_views_are_not_zero_or_forecasts(self):
        views = build_market_views(self.rows)
        self.assertEqual(len(views["role_market_view"]["rows"]), 308)
        for view in ("skill_market_view", "employer_market_view"):
            self.assertEqual(views[view]["status"], "not_supported_by_sources")
            self.assertEqual(views[view]["rows"], [])
        self.assertIsNone(views["market_score_policy"])
        self.assertIsNone(views["overall_recommendation_index"])

    def test_separate_source_country_cohorts_never_share_rankings(self):
        # Hypothetical incompatibility copies, not observations of a second country.
        local = [self.observation(label=name) for name in ("Managers", "Professionals", "Jumlah")]
        other = copy.deepcopy(local)
        for row in other:
            row.update(source_id="synthetic-other-provider", geography_code="USA",
                       source_coverage="hypothetical test coverage", observation_id="test-other-" + row["observation_id"])
        views = build_market_views(local + other)["role_market_view"]
        self.assertEqual(len(views["rankings"]), 2)
        for ranking in views["rankings"]:
            prefix_flags = [identifier.startswith("test-other-") for identifier in ranking["ordered_observation_ids"]]
            self.assertTrue(all(prefix_flags) or not any(prefix_flags))

    def test_frozen_snapshot_repeats_without_mutating_source_or_holdout(self):
        before = {s["relative_path"]: sha(PACK / s["relative_path"]) for s in self.provenance["checksums"]}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sentinel = root / "frozen-holdout.json"
            sentinel.write_text('{"test_sentinel": true}\n')
            digest = sha(sentinel)
            first = prepare_snapshot(output_root=root / "snapshots")
            second = prepare_snapshot(output_root=root / "snapshots")
            self.assertEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertEqual(first["output_sha256"], second["output_sha256"])
            self.assertTrue(second["reused_identical_snapshot"])
            self.assertEqual(validate_snapshot(Path(first["path"]))["validated_rows"], 952)
            self.assertEqual(sha(sentinel), digest)
            target = Path(first["path"]) / "observations.jsonl"
            target.write_text(target.read_text() + " ")
            with self.assertRaises(ValueError):
                prepare_snapshot(output_root=root / "snapshots")
        self.assertEqual(before, {name: sha(PACK / name) for name in before})


if __name__ == "__main__":
    unittest.main()
