"""Canonical entities adapt to the existing five-feature builder, never a new scorer."""

from .data_schemas import VERSION, validate_entity, pending_review
from .review import prepare_profile


def _legacy_review(review):
    return {"review_status": "reviewed" if review["status"] == "approved" else review["status"],
            "reviewer_id": review["reviewer_id"], "review_reason": review["rationale"], "reviewed_at": review["reviewed_at"]}


def _canonical_review(record):
    # Vocabulary adaptation of an existing recorded review, not an approval action.
    return {"status": "approved" if record.get("review_status") == "reviewed" else record.get("review_status", "pending"),
            "reviewer_id": record.get("reviewer_id"), "rationale": record.get("review_reason"), "reviewed_at": record.get("reviewed_at")}


def migrate_pending_roles(catalogue):
    """Map existing worksheet fields without turning source ratings into fit features."""
    roles = []
    for row in catalogue["roles"]:
        source = {"source_id": row["source_id"], "source_version": "O*NET 31.0",
                  "record_id": row["role_id"]}
        criteria = []
        for c in row["criteria"]:
            element = c["source_rows"][0]["element_id"]
            criteria.append({"criterion_id": c["criterion_id"], "skill_id": "onet:" + element,
                             "skill_taxonomy": {"system": "O*NET essential skills", "version": "31.0", "code": element, "label": c["source_skill_name"]},
                             "requirement_weight": c["requirement_weight"], "importance": None, "importance_scale": None,
                             "observable_evidence_rule": c["description"], "sources": [source], "review": _canonical_review(c)})
        estimate = row["effort_estimate"]
        role = {"schema_version": VERSION, "entity_type": "RoleDefinition", "role_id": row["role_id"],
                "version": catalogue["catalogue_version"], "title": row["title"], "preparation_milestone": None,
                "task_interest_tags": [], "criteria": criteria,
                "occupation_identifiers": [{"identifier": {"system": "O*NET-SOC", "version": "31.0", "code": row["role_id"], "label": row["title"]},
                                            "mapping_type": "exact", "scope": "Source identity only; target-country/market use still pending", "sources": [source], "review": pending_review()}],
                "sources": [source], "feature_rubrics": {name: {"definition": r["rubric"], "evidence_rule": None, "review": _canonical_review(r)} for name, r in row["feature_rubrics"].items()},
                "remaining_effort": {"hours_used": estimate["effort_hours_used"], "low_hours": estimate["effort_low_hours"], "high_hours": estimate["effort_high_hours"], "basis": estimate["estimate_basis"], "review": _canonical_review(estimate)},
                "review": _canonical_review(row)}
        validate_entity(role, "RoleDefinition")
        roles.append(role)
    return roles


def derive_profile(profile, roles, include_scores=False):
    validate_entity(profile, "UserProfile")
    if profile["data_class"] != "synthetic":
        raise ValueError("private profiles must not enter public review/training artifacts")
    for role in roles:
        validate_entity(role, "RoleDefinition")
    versions = {r["version"] for r in roles}
    if len(versions) > 1:
        raise ValueError("one catalogue version required per comparison")
    legacy_roles = []
    for role in roles:
        legacy_roles.append({"role_id": role["role_id"], **_legacy_review(role["review"]),
            "mapping_reviewed": bool(role["occupation_identifiers"]) and all(m["review"]["status"] == "approved" for m in role["occupation_identifiers"]),
            "criteria": [{"criterion_id": c["criterion_id"], "requirement_weight": c["requirement_weight"], **_legacy_review(c["review"])} for c in role["criteria"]],
            "feature_rubrics": {name: _legacy_review(r["review"]) for name, r in role["feature_rubrics"].items()},
            "effort_estimate": {"effort_hours_used": role["remaining_effort"]["hours_used"], "effort_low_hours": role["remaining_effort"]["low_hours"], "effort_high_hours": role["remaining_effort"]["high_hours"], **_legacy_review(role["remaining_effort"]["review"])},
            "evidence_ids": sorted({s["source_id"] for s in role["sources"]})})
    observations = []
    for role in roles:
        for criterion in role["criteria"]:
            matches = [s for s in profile["skill_observations"] if s["skill_id"] == criterion["skill_id"]
                       and s["criterion_id"] == criterion["criterion_id"] and s["role_id"] == role["role_id"]
                       and s["state"] in ("assessed", "demonstrated") and s["review"]["status"] == "approved"]
            if len(matches) > 1:
                raise ValueError("ambiguous multiple approved criterion observations")
            if matches:
                s = matches[0]
                observations.append({"role_id": role["role_id"], "criterion_id": criterion["criterion_id"], "demonstrated_fraction": s["demonstrated_fraction"], "evidence_ids": s["evidence_ids"], **_legacy_review(s["review"])})
    legacy_profile = {"profile_id": profile["profile_id"], "profile_group_id": profile["profile_family_id"],
                      "profile_version": profile["version"], "profile_is_synthetic": True,
                      "preparation_horizon_weeks": profile["planning_horizon"]["weeks"], "hours_per_week": profile["hours_per_week"],
                      "criterion_assessments": observations,
                      "role_assessments": [{k: v for k, v in r.items() if k != "review"} | _legacy_review(r["review"]) for r in profile["role_alignments"]]}
    for alignment in legacy_profile["role_assessments"]:
        if profile["interests"] is None:
            alignment["interest_alignment"] = None
        if profile["work_preferences"] is None:
            alignment["work_style_alignment"] = None
        if profile["access_budget_constraints"]["resources"] is None:
            alignment["resource_feasibility"] = None
    catalogue = {"catalogue_version": next(iter(versions), "empty-catalogue"), "evidence_snapshot_id": "canonical-review-v1", "roles": legacy_roles}
    output = prepare_profile(legacy_profile, catalogue, include_scores=include_scores)
    by_id = {r["role_id"]: r for r in roles}
    for sidecar in output["roles"]:
        criteria = {c["criterion_id"]: c for c in by_id[sidecar["role_id"]]["criteria"]}
        for gap in sidecar["criterion_gaps"]:
            criterion = criteria[gap["criterion_id"]]
            gap["skill_id"] = criterion["skill_id"]
            gap["source_ids"] = sorted({s["source_id"] for s in criterion["sources"]})
    return output
