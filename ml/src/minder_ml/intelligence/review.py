"""Reviewed raw inputs to shared features/service; no inferred facts or approvals."""

from dataclasses import asdict

from .features import build_features, criterion_gaps
from .inference import recommend
from .schemas import RoleInput, nonempty, number


def _reviewed(record):
    return (record.get("review_status") == "reviewed"
            and all(isinstance(record.get(k), str) and record[k].strip()
                    for k in ("reviewer_id", "review_reason", "reviewed_at")))


def prepare_profile(profile, catalogue, *, include_scores=True):
    """Return a derivation/gap sidecar and the unchanged recommendation-v1 result.

    A catalogue's source existence does not approve its initial milestone criteria.
    Raw profile and assessments must be supplied; normalized example vectors cannot
    be reverse-engineered into skill evidence, effort estimates or user preferences.
    """
    if profile.get("profile_is_synthetic") is not True:
        raise ValueError("only explicitly synthetic profiles are authorized")
    for key in ("profile_id", "profile_group_id", "profile_version"):
        nonempty(profile.get(key), key)
    nonempty(catalogue.get("catalogue_version"), "catalogue_version")
    nonempty(catalogue.get("evidence_snapshot_id"), "evidence_snapshot_id")
    horizon = number(profile.get("preparation_horizon_weeks"), "preparation_horizon_weeks")
    if horizon <= 0:
        raise ValueError("positive preparation horizon required")
    assessments = {}
    for item in profile.get("criterion_assessments", []):
        key = (item["role_id"], item["criterion_id"])
        if key in assessments:
            raise ValueError("duplicate criterion assessment")
        assessments[key] = item
    role_reviews = {}
    for item in profile.get("role_assessments", []):
        if item["role_id"] in role_reviews:
            raise ValueError("duplicate role assessment")
        role_reviews[item["role_id"]] = item
    sidecars, inputs, blocked = [], [], []
    seen_roles = set()
    for role in catalogue["roles"]:
        role_id = nonempty(role["role_id"], "role_id")
        if role_id in seen_roles:
            raise ValueError("duplicate catalogue role")
        seen_roles.add(role_id)
        criteria = role.get("criteria", [])
        blockers = []
        if not _reviewed(role):
            blockers.append("role_milestone_review_pending")
        if not criteria or any(not _reviewed(c) for c in criteria):
            blockers.append("criterion_review_pending")
        if role.get("mapping_reviewed") is not True:
            blockers.append("source_mapping_review_pending")
        review = role_reviews.get(role_id, {})
        rubric_names = ("interest_alignment", "resource_feasibility", "work_style_alignment")
        if any(not _reviewed(role.get("feature_rubrics", {}).get(n, {})) for n in rubric_names):
            blockers.append("feature_rubric_review_pending")
        if not _reviewed(role.get("effort_estimate", {})):
            blockers.append("effort_estimate_review_pending")
        if blockers:
            blocked.append({"role_id": role_id, "reasons": blockers})
            sidecars.append({"role_id": role_id, "readiness": "pending_review",
                             "feature_components": None, "evidence_coverage": None,
                             "criterion_gaps": [{"criterion_id": c["criterion_id"],
                                                 "remaining_fraction": None,
                                                 "reason": "unreviewed_catalogue"} for c in criteria]})
            continue
        requirements, evidence_ids = [], list(role.get("evidence_ids", []))
        for criterion in criteria:
            assessment = assessments.get((role_id, criterion["criterion_id"]), {})
            fraction = assessment.get("demonstrated_fraction") if _reviewed(assessment) else None
            requirements.append({"criterion_id": criterion["criterion_id"],
                                 "requirement_weight": criterion["requirement_weight"],
                                 "demonstrated_fraction": fraction})
            evidence_ids.extend(assessment.get("evidence_ids", []) if _reviewed(assessment) else [])
        values = {n: review.get(n) if _reviewed(review) else None for n in rubric_names}
        estimate = role["effort_estimate"]
        snapshot = build_features(
            [(r["requirement_weight"], r["demonstrated_fraction"]) for r in requirements],
            values["interest_alignment"], values["resource_feasibility"], values["work_style_alignment"],
            profile.get("hours_per_week"), estimate.get("effort_hours_used"), horizon,
            estimate.get("effort_low_hours"), estimate.get("effort_high_hours"))
        gaps = criterion_gaps(requirements)
        sidecars.append({"role_id": role_id, "readiness": "feature_complete" if snapshot.eligible else "missing_profile_evidence",
                         "feature_snapshot": asdict(snapshot), "criterion_gaps": gaps})
        evidence_ids.extend(review.get("evidence_ids", []) if _reviewed(review) else [])
        inputs.append(RoleInput(role_id, snapshot, sorted(set(evidence_ids))))
    output = {"derivation_schema_version": "profile-feature-review-v1", "roles": sidecars,
            "blocked_roles": blocked,
            "scope": "Only reviewed catalogue inputs enter the existing service; blocked roles are listed separately."}
    if include_scores:
        result = recommend(inputs, profile_version=profile["profile_version"],
                           evidence_snapshot_id=catalogue["evidence_snapshot_id"],
                           role_catalogue_version=catalogue["catalogue_version"],
                           preparation_horizon_weeks=horizon)
        output["recommendation"] = result.to_dict()
    return output
