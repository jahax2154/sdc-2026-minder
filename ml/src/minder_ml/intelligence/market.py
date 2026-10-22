"""Indicator-specific comparisons. No scalar market score or demand forecasting."""

from datetime import date
import json
from .data_schemas import validate_entity


def comparability_key(row):
    return {k: row[k] for k in (
        "indicator_id", "unit", "source_id", "source_version", "source_coverage",
        "population_coverage", "measurement_method", "methodology_version",
        "taxonomy_system", "taxonomy_version", "geography_code", "geography_level",
        "region_code", "frequency", "dimension_scope", "measurement_kind")}


def compare_observations(current, previous, mode="yoy"):
    if mode not in ("yoy", "share", "cohort"):
        raise ValueError("unsupported comparison mode")
    validate_entity(current, "MarketObservation")
    validate_entity(previous, "MarketObservation")
    reasons = []
    left, right = comparability_key(current), comparability_key(previous)
    for key in left:
        if left[key] != right[key]:
            reasons.append(key + "_mismatch")
    if current["geography_code"] != previous["geography_code"]:
        reasons.append("cross_country_or_geography_normalization_not_approved")
    if current["source_id"] != previous["source_id"] or current["source_coverage"] != previous["source_coverage"]:
        reasons.append("different_provider_counts_are_not_national_market_sizes")
    if ((current["denominator"] or {}).get("meaning") != (previous["denominator"] or {}).get("meaning")):
        reasons.append("denominator_meaning_mismatch")
    if current["measurement_kind"] != "observed" or previous["measurement_kind"] != "observed":
        reasons.append("requires_observed_values")
    if current["value"] is None or previous["value"] is None:
        reasons.append("missing_observation")
    if current["data_quality_status"] == "invalid" or previous["data_quality_status"] == "invalid":
        reasons.append("invalid_observation")
    if mode == "yoy":
        if current["frequency"] != "quarterly" or previous["frequency"] != "quarterly":
            reasons.append("yoy_requires_quarterly_observations")
        a, b = date.fromisoformat(current["period_start"]), date.fromisoformat(previous["period_start"])
        if not (a.year == b.year + 1 and a.month == b.month and a.day == b.day):
            reasons.append("not_exactly_four_quarters_apart")
        for field in ("occupation_code", "occupation_label", "skill_id", "employer_id", "industry_id", "industry_label", "group_kind"):
            if current[field] != previous[field]:
                reasons.append("series_identity_mismatch")
        if current["value"] is not None and previous["value"] is not None and previous["value"] <= 0:
            reasons.append("nonpositive_yoy_denominator")
        if "classification_coverage_review" in current["quality_flags"] + previous["quality_flags"]:
            reasons.append("classification_continuity_requires_review")
    else:
        if (current["period_start"], current["period_end"]) != (previous["period_start"], previous["period_end"]):
            reasons.append("observation_windows_mismatch")
        if mode == "share":
            if previous["group_kind"] != "overall":
                reasons.append("share_denominator_must_be_published_total")
            if previous["value"] is not None and previous["value"] <= 0:
                reasons.append("nonpositive_share_denominator")
            if current["value"] is not None and previous["value"] is not None and current["value"] > previous["value"]:
                reasons.append("part_exceeds_published_total")
    return {"comparable": not reasons, "reasons": sorted(set(reasons)), "mode": mode}


def observed_yoy(current, previous):
    check = compare_observations(current, previous, "yoy")
    return {"value": 100 * (current["value"] / previous["value"] - 1) if check["comparable"] else None,
            "unit": "percent_change", "reference_observation_id": previous["observation_id"], **check}


def observed_share(current, total):
    check = compare_observations(current, total, "share")
    return {"value": current["value"] / total["value"] if check["comparable"] else None,
            "denominator_observation_id": total["observation_id"],
            "denominator_value": total["value"], "meaning": "share of published observed source total", **check}


def build_market_views(rows):
    """One canonical table; unsupported dimensions remain unsupported, never zeros."""
    for row in rows:
        validate_entity(row, "MarketObservation")
    def scope(row):
        return json.dumps([comparability_key(row), (row["denominator"] or {}).get("meaning")], sort_keys=True)
    totals = {(scope(r), r["period_start"], r["period_end"]): r for r in rows if r["group_kind"] == "overall"}
    series = {(scope(r), r["occupation_code"], r["occupation_label"], r["industry_id"], r["industry_label"], r["period_start"]): r for r in rows}
    role_rows = []
    for row in rows:
        if row["dimension_scope"] != "occupation":
            continue
        start = date.fromisoformat(row["period_start"])
        prior = series.get((scope(row), row["occupation_code"], row["occupation_label"], row["industry_id"], row["industry_label"], date(start.year - 1, start.month, 1).isoformat()))
        total = totals.get((scope(row), row["period_start"], row["period_end"]))
        share = observed_share(row, total) if total and row["group_kind"] != "overall" else {
            "value": None, "reason": "published_total_is_not_a_category_share"}
        growth = observed_yoy(row, prior) if prior else {"value": None, "reasons": ["missing_exact_prior_year_quarter"]}
        role_rows.append({"observation": row, "observed_offering_count": row["value"],
                          "observed_source_share": share, "observed_yoy_change": growth})
    role_rows.sort(key=lambda r: (scope(r["observation"]), r["observation"]["period_start"], r["observation"]["occupation_label"] or ""))
    cohorts = {}
    for row in role_rows:
        observation = row["observation"]
        if observation["group_kind"] == "category" and row["observed_offering_count"] is not None:
            cohorts.setdefault((scope(observation), observation["period_start"], observation["period_end"]), []).append(row)
    rankings = []
    for _, cohort in sorted(cohorts.items()):
        if any(not compare_observations(cohort[0]["observation"], r["observation"], "cohort")["comparable"] for r in cohort):
            raise ValueError("ranking cohort is not comparable")
        ordered = sorted(cohort, key=lambda r: (-r["observed_offering_count"], r["observation"]["occupation_label"] or ""))
        observation = ordered[0]["observation"]
        rankings.append({"comparability_key": comparability_key(observation), "period_start": observation["period_start"],
                         "period_end": observation["period_end"], "scope": "Published observed online offering counts, broad occupation groups only",
                         "not_hires_or_fine_grained_role_demand": True,
                         "ordered_observation_ids": [r["observation"]["observation_id"] for r in ordered]})
    unsupported = lambda reason: {"status": "not_supported_by_sources", "reason": reason, "rows": []}
    return {
        "role_market_view": {"status": "supported_at_published_occupation_major_group_level", "rows": role_rows,
                             "rankings": rankings},
        "skill_market_view": unsupported("No verified skill-tagged posting source acquired; taxonomy associations are not measured skill demand."),
        "employer_market_view": unsupported("No authorized employer-level posting source acquired; posting activity would not establish company hiring volume."),
        "market_score_policy": None, "overall_recommendation_index": None}
