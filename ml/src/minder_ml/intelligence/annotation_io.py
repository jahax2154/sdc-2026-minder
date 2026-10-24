"""Blinded human review I/O. Weak proposals never become gold or holdout rows."""

from collections import defaultdict
import copy
import csv
import hashlib
import io
import json
from pathlib import Path

from .data_adapters import derive_profile
from .data_pipeline import encoded, sha
from .data_schemas import VERSION, validate_entity
from .evaluation import ANNOTATION_COLUMNS
from .schemas import FEATURE_VERSION, RUBRIC_VERSION


def _hash(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def write_bundle(target, files):
    target = Path(target)
    if target.exists():
        if any(not (target / name).is_file() or (target / name).read_text() != text for name, text in files.items()):
            raise ValueError("refusing to overwrite frozen review artifacts; use a new versioned output path")
    else:
        target.mkdir(parents=True, exist_ok=False)
        for name, text in files.items():
            with (target / name).open("x") as stream:
                stream.write(text)


def export_annotations(profiles, roles, output):
    for profile in profiles:
        validate_entity(profile, "UserProfile")
        if profile["data_class"] != "synthetic":
            raise ValueError("private profiles cannot be exported into public review artifacts")
    for role in roles:
        validate_entity(role, "RoleDefinition")
    if len({p["profile_id"] for p in profiles}) != len(profiles) or len({r["role_id"] for r in roles}) != len(roles):
        raise ValueError("duplicate profiles or roles")
    inputs = {"profiles": profiles, "roles": roles}
    packet_id = _hash(inputs)
    pairs, templates, features = [], [], []
    for profile in sorted(profiles, key=lambda p: p["profile_id"]):
        derived = derive_profile(profile, roles, include_scores=False)
        sidecars = {r["role_id"]: r for r in derived["roles"]}
        for role in sorted(roles, key=lambda r: r["role_id"]):
            pair_id = _hash([packet_id, profile["profile_id"], role["role_id"]])[:24]
            visible_profile = copy.deepcopy(profile)
            visible_profile.pop("role_alignments")  # Hide normalized I/R/W judgments during initial grading.
            pairs.append({"pair_id": pair_id, "profile_evidence": visible_profile, "role_requirements": role,
                          "grading_status": "ready_for_independent_review" if role["review"]["status"] == "approved" else "blocked_pending_role_review"})
            template = {"schema_version": VERSION, "entity_type": "PersonalFitAnnotation",
                        "annotation_id": pair_id + "-pending", "pair_id": pair_id,
                        "profile_id": profile["profile_id"], "profile_version": profile["version"],
                        "role_id": role["role_id"], "role_version": role["version"],
                        "rubric_version": RUBRIC_VERSION, "feature_schema_version": FEATURE_VERSION,
                        "preparation_horizon": profile["planning_horizon"]["weeks"], "grade": None,
                        "reviewer_id": None, "rationale": None, "review_status": "pending", "reviewed_at": None,
                        "profile_family_id": profile["profile_family_id"], "label_source": None,
                        "independent_review": None, "rubric_ambiguity": None}
            validate_entity(template, "PersonalFitAnnotation")
            templates.append(template)
            features.append({"pair_id": pair_id, "profile_id": profile["profile_id"],
                             "role_id": role["role_id"], "derivation": sidecars[role["role_id"]]})
    packet = {"schema_version": "blind-review-packet-v1", "packet_id": packet_id,
              "rubric": {"0": "weak preparation relevance", "1": "plausible preparation pathway", "2": "strong preparation relevance"},
              "instructions": "Grade independently under the stated horizon, excluding market attractiveness. Leave unresolved judgments blank. Do not consult engineering feature files or algorithm outputs. Role acceptance is not a target label.",
              "pairs": pairs}
    manifest = {"packet_sha256": _hash(packet), "engineering_inputs_sha256": _hash(inputs)}
    review_manifest = {"packet_id": packet_id, "schema_version": VERSION,
                       "roles": [{"role_id": r["role_id"], "version": r["version"], "review": r["review"], "sources": r["sources"]} for r in roles],
                       "profiles": [{"profile_id": p["profile_id"], "profile_family_id": p["profile_family_id"], "version": p["version"], "data_class": p["data_class"], "review": p["review"]} for p in profiles]}
    write_bundle(output, {"packet.json": encoded(packet), "responses.template.json": encoded(templates),
                          "engineering_features.json": encoded(features), "engineering_inputs.json": encoded(inputs),
                          "packet_manifest.json": encoded(manifest), "review_manifest.json": encoded(review_manifest)})
    return {"packet_id": packet_id, "output": str(output), "pairs": len(pairs),
            "approved_roles": sum(r["review"]["status"] == "approved" for r in roles),
            "profile_families": len({p["profile_family_id"] for p in profiles}),
            "approved_profile_families": len({p["profile_family_id"] for p in profiles if p["review"]["status"] == "approved"}),
            "gold_labels": 0, "baseline_scores_exposed": False}


def import_annotations(packet_dir, response_path, output):
    packet_dir = Path(packet_dir)
    packet = json.loads((packet_dir / "packet.json").read_text())
    inputs = json.loads((packet_dir / "engineering_inputs.json").read_text())
    manifest = json.loads((packet_dir / "packet_manifest.json").read_text())
    if _hash(packet) != manifest["packet_sha256"] or _hash(inputs) != manifest["engineering_inputs_sha256"]:
        raise ValueError("public packet or engineering input fingerprint changed")
    if _hash(inputs) != packet["packet_id"]:
        raise ValueError("packet input fingerprint changed")
    profiles = {p["profile_id"]: p for p in inputs["profiles"]}
    roles = {r["role_id"]: r for r in inputs["roles"]}
    for profile in profiles.values():
        validate_entity(profile, "UserProfile")
        if profile["data_class"] != "synthetic":
            raise ValueError("private profile in public packet")
    for role in roles.values():
        validate_entity(role, "RoleDefinition")
    expected = {}
    derived = {}
    for profile in profiles.values():
        result = derive_profile(profile, list(roles.values()), include_scores=False)
        for item in result["roles"]:
            pair_id = _hash([packet["packet_id"], profile["profile_id"], item["role_id"]])[:24]
            expected[pair_id] = (profile, roles[item["role_id"]])
            derived[pair_id] = item
    if {p["pair_id"] for p in packet["pairs"]} != set(expected):
        raise ValueError("packet pair set changed")
    responses = json.loads(Path(response_path).read_text())
    if not isinstance(responses, list):
        raise ValueError("response file must be an annotation array")
    by_pair, seen_ids, seen_reviewers = defaultdict(list), set(), set()
    for row in responses:
        validate_entity(row, "PersonalFitAnnotation")
        if row["annotation_id"] in seen_ids or row["pair_id"] not in expected:
            raise ValueError("duplicate annotation or unknown pair")
        seen_ids.add(row["annotation_id"])
        profile, role = expected[row["pair_id"]]
        matching = {"profile_id": profile["profile_id"], "profile_version": profile["version"],
                    "profile_family_id": profile["profile_family_id"], "role_id": role["role_id"],
                    "role_version": role["version"], "preparation_horizon": profile["planning_horizon"]["weeks"]}
        if any(row[k] != v for k, v in matching.items()):
            raise ValueError("response immutable profile/role/family/horizon context changed")
        reviewer_key = (row["pair_id"], row["reviewer_id"])
        if row["reviewer_id"] and reviewer_key in seen_reviewers:
            raise ValueError("duplicate reviewer judgment for one pair")
        seen_reviewers.add(reviewer_key)
        by_pair[row["pair_id"]].append(row)
    gold, disagreements, unresolved = [], [], []
    for pair_id, (profile, role) in sorted(expected.items()):
        votes = [r for r in by_pair[pair_id] if r["review_status"] == "approved"
                 and r["label_source"] == "human_reviewed" and r["independent_review"] is True]
        grades = {r["grade"] for r in votes}
        if len(grades) > 1:
            disagreements.append({"pair_id": pair_id, "grades": sorted(grades), "reviewer_ids": sorted(r["reviewer_id"] for r in votes)})
        feature_ready = derived[pair_id]["readiness"] == "feature_complete"
        if len(grades) == 1 and feature_ready and role["review"]["status"] == "approved" and not any(r["rubric_ambiguity"] for r in by_pair[pair_id]):
            # Preserve one original agreeing judgment, never average or generate a label.
            gold.append(sorted(votes, key=lambda r: r["annotation_id"])[0])
        else:
            unresolved.append({"pair_id": pair_id, "no_independent_human_grade": not votes,
                               "disagreement": len(grades) > 1, "features_ready": feature_ready,
                               "role_approved": role["review"]["status"] == "approved",
                               "rubric_ambiguity": any(bool(r["rubric_ambiguity"]) for r in by_pair[pair_id])})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=ANNOTATION_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in gold:
        snapshot = derived[row["pair_id"]]["feature_snapshot"]
        writer.writerow({"profile_id": row["profile_id"], "profile_group_id": row["profile_family_id"],
                         "role_id": row["role_id"], "profile_version": row["profile_version"],
                         "role_catalogue_version": row["role_version"], "feature_schema_version": FEATURE_VERSION,
                         "rubric_version": RUBRIC_VERSION, "reviewer_id": row["reviewer_id"], "review_reason": row["rationale"],
                         "profile_is_synthetic": "true", "reviewer_independent": "true",
                         "preparation_horizon_weeks": row["preparation_horizon"], "annotation_status": "reviewed",
                         "relevance_grade": row["grade"], **{name: snapshot[name] for name in ANNOTATION_COLUMNS if name in snapshot}})
    report = {"packet_id": packet["packet_id"], "response_sha256": sha(response_path), "response_rows": len(responses),
              "validated_rows": len(responses), "rejected_rows": 0,
              "approved_roles": sum(r["review"]["status"] == "approved" for r in roles.values()),
              "profile_families": len({p["profile_family_id"] for p in profiles.values()}),
              "approved_profile_families": len({p["profile_family_id"] for p in profiles.values() if p["review"]["status"] == "approved"}),
              "pending_rows": sum(r["review_status"] == "pending" for r in responses),
              "weak_proposals": sum(r["label_source"] == "weak_auto_proposal" for r in responses),
              "independent_human_approved_rows": sum(r["label_source"] == "human_reviewed" and r["review_status"] == "approved" for r in responses),
              "gold_labels": len(gold), "disagreements": disagreements, "unresolved_cases": unresolved,
              "empirical_status": "not_evaluated", "note": "Structural provenance validation is not proof that human review occurred. No scores or automatic labels generated."}
    write_bundle(output, {"responses.json": encoded(responses), "gold_annotations.json": encoded(gold),
                          "weak_auto_proposals.json": encoded([r for r in responses if r["label_source"] == "weak_auto_proposal"]),
                          "foundation_annotations.csv": stream.getvalue(), "readiness.json": encoded(report)})
    return report
