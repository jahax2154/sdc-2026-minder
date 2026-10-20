"""Reviewed snapshot validation, grouped partitions and served-order diagnostics."""

from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random

from .features import feature_matrix
from .schemas import FEATURE_NAMES, FEATURE_VERSION, RUBRIC_VERSION, FeatureSnapshot, number, nonempty
from .scoring import baseline, learned_score

PROVENANCE = ("profile_id", "profile_group_id", "role_id", "profile_version",
              "role_catalogue_version", "feature_schema_version", "rubric_version",
              "reviewer_id", "review_reason")
ANNOTATION_COLUMNS = list(PROVENANCE) + [
    "profile_is_synthetic", "reviewer_independent", "preparation_horizon_weeks",
    "annotation_status", "relevance_grade", *FEATURE_NAMES, "assessed_requirement_fraction"]


def read_annotations(path):
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        columns = reader.fieldnames or []
    accepted, errors = [], []
    pending = 0
    profiles = set()
    groups = set()
    profile_meta = {}
    seen = set()
    for line, row in enumerate(rows, 2):
        profiles.add(row.get("profile_id", ""))
        groups.add(row.get("profile_group_id", ""))
        if row.get("annotation_status") == "pending" and not row.get("relevance_grade", "").strip():
            pending += 1
            continue
        try:
            if row.get("annotation_status") != "reviewed":
                raise ValueError("grade requires annotation_status=reviewed; pending grades must remain blank")
            for field in PROVENANCE:
                nonempty(row.get(field), field)
            if row["feature_schema_version"] != FEATURE_VERSION or row["rubric_version"] != RUBRIC_VERSION:
                raise ValueError("incompatible feature or target rubric version")
            if row.get("reviewer_independent") != "true":
                raise ValueError("independent review must be explicitly attested")
            if row.get("profile_is_synthetic") not in ("true", "false"):
                raise ValueError("profile_is_synthetic must be true or false")
            # The repository's competition constraints exclude real personal data.
            if row["profile_is_synthetic"] != "true":
                raise ValueError("this prototype accepts explicitly synthetic profiles only")
            if row.get("relevance_grade") not in ("0", "1", "2"):
                raise ValueError("reviewed relevance_grade must be integer 0, 1 or 2")
            converted = dict(row)
            converted["profile_is_synthetic"] = row["profile_is_synthetic"] == "true"
            converted["reviewer_independent"] = True
            converted["relevance_grade"] = int(row["relevance_grade"])
            converted["preparation_horizon_weeks"] = number(float(row["preparation_horizon_weeks"]), "horizon")
            if converted["preparation_horizon_weeks"] <= 0:
                raise ValueError("positive preparation horizon required")
            for name in (*FEATURE_NAMES, "assessed_requirement_fraction"):
                converted[name] = float(row[name]) if row.get(name, "").strip() else None
            snapshot = FeatureSnapshot.from_dict(converted)
            snapshot.vector()
            converted["snapshot"] = snapshot
            key = (row["profile_id"], row["role_id"])
            if key in seen:
                raise ValueError("duplicate profile-role annotation")
            pm = (row["profile_group_id"], row["profile_version"])
            if row["profile_id"] in profile_meta and profile_meta[row["profile_id"]] != pm:
                raise ValueError("profile variants/version assigned inconsistently")
            profile_meta[row["profile_id"]] = pm
            seen.add(key)
            accepted.append(converted)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({"line": line, "error": str(exc)})
    compatibility = {(r["preparation_horizon_weeks"], r["role_catalogue_version"]) for r in accepted}
    if len(compatibility) > 1:
        errors.append({"error": "mixed horizon or catalogue versions; separate comparison runs required"})
    report = {"rows": len(rows), "profile_count": len(profiles - {""}),
              "profile_group_count": len(groups - {""}), "pending_rows": pending,
              "eligible_reviewed_rows": len(accepted),
              "eligible_reviewed_groups": len({r["profile_group_id"] for r in accepted}),
              "missing_columns": sorted(set(ANNOTATION_COLUMNS) - set(columns)),
              "errors": errors, "empirical_status": "not_evaluated"}
    report["candidate_coverage_by_profile"] = {
        profile: {"annotation_rows": sum(r.get("profile_id") == profile for r in rows),
                  "eligible_reviewed_rows": sum(r["profile_id"] == profile for r in accepted)}
        for profile in sorted(profiles - {""})}
    return accepted, report


def compatibility(rows):
    return {"preparation_horizon_weeks": rows[0]["preparation_horizon_weeks"],
            "role_catalogue_version": rows[0]["role_catalogue_version"]}


def split_groups(rows, supplied=None):
    groups = sorted({r["profile_group_id"] for r in rows})
    if supplied is None:
        shuffled = groups[:]
        random.Random(42).shuffle(shuffled)
        # Small sets get exploratory grouped CV, never a random row split.
        holdout_count = max(1, len(groups) // 5) if len(groups) >= 5 else 0
        supplied = {"seed": 42, "development": sorted(shuffled[holdout_count:]),
                    "holdout": sorted(shuffled[:holdout_count])}
    dev, hold = supplied.get("development", []), supplied.get("holdout", [])
    if (not isinstance(dev, list) or not isinstance(hold, list)
            or len(set(dev)) != len(dev) or len(set(hold)) != len(hold)
            or set(dev) & set(hold) or set(dev) | set(hold) != set(groups) or not dev):
        raise ValueError("split must assign every group once with no overlap")
    return {"seed": 42, "development": sorted(dev), "holdout": sorted(hold)}


def partition(rows, split, name):
    return [r for r in rows if r["profile_group_id"] in split[name]]


def snapshots_hash(rows):
    serial = [{k: v for k, v in r.items() if k != "snapshot"} for r in rows]
    return hashlib.sha256(json.dumps(serial, sort_keys=True, allow_nan=False).encode()).hexdigest()


def predictions(kind, model, rows):
    if kind == "baseline":
        return [baseline(r["snapshot"]) / 50 for r in rows]
    from .artifacts import predict_raw
    return predict_raw(model, feature_matrix([r["snapshot"] for r in rows]))


def diagnostics(rows, raw_predictions):
    if len(rows) != len(raw_predictions) or not rows:
        raise ValueError("nonempty aligned predictions required")
    by_profile = defaultdict(list)
    absolute_errors, clipped = [], 0
    for row, raw in zip(rows, raw_predictions):
        score = learned_score(float(raw))
        clipped += int(raw < 0 or raw > 2)
        absolute_errors.append(abs(score / 50 - row["relevance_grade"]))
        by_profile[row["profile_id"]].append((row["role_id"], row["relevance_grade"], score))
    records, ndcgs = [], []
    all_weak, tied_pairs = [], 0
    for profile, values in sorted(by_profile.items()):
        ordered = sorted(values, key=lambda v: (-v[2], v[0]))
        ideal = sorted(values, key=lambda v: (-v[1], v[0]))
        dcg = sum(v[1] / math.log2(i + 2) for i, v in enumerate(ordered[:3]))
        idcg = sum(v[1] / math.log2(i + 2) for i, v in enumerate(ideal[:3]))
        ndcg = dcg / idcg if idcg > 0 else None
        ties = sum(a[2] == b[2] for i, a in enumerate(ordered) for b in ordered[i + 1:])
        tied_pairs += ties
        if ndcg is None:
            all_weak.append(profile)
        else:
            ndcgs.append(ndcg)
        records.append({"profile_id": profile, "candidate_count": len(values),
                        "eligible_candidate_coverage": 1.0, "ndcg_at_3": ndcg,
                        "idcg_at_3": idcg, "score_tie_pairs": ties,
                        "served_role_order": [v[0] for v in ordered]})
    return {"rows": len(rows), "profile_count": len(by_profile),
            "mean_ndcg_at_3": sum(ndcgs) / len(ndcgs) if ndcgs else None,
            "mae_served_grade": sum(absolute_errors) / len(rows),
            "clipping_rate": clipped / len(rows), "score_tie_pairs": tied_pairs,
            "idcg_zero_profiles": all_weak, "per_profile": records,
            "candidate_set": "same complete eligible reviewed rows for all scorers"}


def counterfactuals(kind, model, rows, limit=20):
    """Bounded diagnostics, not an empirical monotonicity guarantee for learners."""
    from .artifacts import predict_raw
    vectors = feature_matrix([r["snapshot"] for r in rows[:limit]])
    def score(x):
        if kind == "baseline":
            from .scoring import BASELINE_WEIGHTS
            return [100 * sum(a * b for a, b in zip(BASELINE_WEIGHTS, v)) for v in x]
        return [learned_score(v) for v in predict_raw(model, x)]
    base = score(vectors)
    modified, refs = [], []
    for i, vector in enumerate(vectors):
        for j, name in enumerate(FEATURE_NAMES):
            if vector[j] < 1:
                changed = vector[:]
                changed[j] = min(1.0, changed[j] + 0.1)
                modified.append(changed)
                refs.append((i, name))
    scores = score(modified) if modified else []
    reversals = [{"profile_id": rows[i]["profile_id"], "role_id": rows[i]["role_id"],
                  "feature": name, "before": base[i], "after": value}
                 for (i, name), value in zip(refs, scores) if value < base[i] - 1e-9]
    return {"rows_checked": len(vectors), "perturbations": len(modified),
            "increment": 0.1, "reversals": reversals,
            "interpretation": "Reversals warrant review/continued baseline use; no constraints tuned."}
