"""Callable application boundary; no framework/bootstrap, training or network."""

from typing import List, Optional
from dataclasses import asdict
from . import artifacts
from .features import feature_matrix
from .schemas import (FEATURE_VERSION, SCORE_VERSION, RANKING_VERSION, RESULT_VERSION,
                      RecommendationResult, RoleInput, RoleResult, nonempty, number)
from .scoring import baseline, learned_score


def recommend(roles: List[RoleInput], *, profile_version: str, evidence_snapshot_id: str,
              role_catalogue_version: str, preparation_horizon_weeks: float = 12,
              scorer_kind: str = "baseline", model_version: Optional[str] = None
              ) -> RecommendationResult:
    if scorer_kind not in ("baseline", "ridge", "xgboost"):
        raise ValueError("unknown scorer_kind")
    for name, value in [("profile_version", profile_version),
                        ("evidence_snapshot_id", evidence_snapshot_id),
                        ("role_catalogue_version", role_catalogue_version)]:
        nonempty(value, name)
    number(preparation_horizon_weeks, "preparation_horizon_weeks")
    if preparation_horizon_weeks <= 0:
        raise ValueError("preparation horizon must be positive")
    if len({r.role_id for r in roles}) != len(roles):
        raise ValueError("duplicate role_id in comparison set")
    if any(r.features.preparation_horizon_weeks != preparation_horizon_weeks for r in roles):
        raise ValueError("feature snapshot horizon differs from requested horizon; rebuild features")
    if scorer_kind == "baseline" and model_version is not None:
        raise ValueError("baseline does not accept a trained model version")
    result = RecommendationResult(
        RESULT_VERSION, profile_version, FEATURE_VERSION, scorer_kind,
        "fixed-baseline-v1" if scorer_kind == "baseline" else model_version,
        SCORE_VERSION, RANKING_VERSION, evidence_snapshot_id, role_catalogue_version,
        "personal_fit_only", 0.7, preparation_horizon_weeks, "completed", [], [], [])
    model = None
    if scorer_kind != "baseline":
        try:
            if not model_version:
                raise ValueError("no artifact selected")
            model = artifacts.load_candidate(model_version, scorer_kind, {
                "preparation_horizon_weeks": preparation_horizon_weeks,
                "role_catalogue_version": role_catalogue_version})
        except (OSError, ValueError, KeyError, ImportError, TypeError) as exc:
            result.result_kind = "model_not_ready"
            result.warnings.append("Requested scorer has no compatible evaluated artifact.")
    eligible = [r for r in roles if r.features.eligible]
    predictions = {}
    if result.result_kind != "model_not_ready":
        if scorer_kind == "baseline":
            predictions = {r.role_id: baseline(r.features) / 50 for r in eligible}
        elif eligible:
            raw = artifacts.predict_raw(model, feature_matrix([r.features for r in eligible]))
            if len(raw) != len(eligible):
                raise ValueError("invalid model output length")
            predictions = dict(zip([r.role_id for r in eligible], raw))
    for role in roles:
        reason = ("insufficient_information" if not role.features.eligible else
                  "model_not_ready" if result.result_kind == "model_not_ready" else None)
        raw = predictions.get(role.role_id)
        option = RoleResult(role.role_id, learned_score(raw) if raw is not None else None,
                            None, None, role.features.assessed_requirement_fraction,
                            role.features.components(), list(role.evidence_ids), raw,
                            asdict(role.features.preparation_evidence) if role.features.preparation_evidence else None,
                            reason)
        (result.unscored_roles if reason else result.options).append(option)
    result.options.sort(key=lambda r: (-r.personal_fit_index, r.role_id))
    result.unscored_roles.sort(key=lambda r: r.role_id)
    if result.result_kind != "model_not_ready" and not result.options:
        result.result_kind = "insufficient_information"
    if len(result.options) < 3:
        result.warnings.append(f"Only {len(result.options)} roles scored; insufficient complete eligible inputs or model unavailable.")
    result.warnings.append("No comparable market index supplied; D and S are null for the entire set.")
    return result
