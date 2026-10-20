"""One feature interpretation for reviewed snapshots, training and inference."""

import math
from .schemas import FeatureSnapshot, PreparationEvidence, number


def skill_coverage(requirements):
    """Reviewed (weight, demonstrated fraction or None) pairs, initial milestone only."""
    if not requirements:
        raise ValueError("invalid_requirement_catalogue: empty catalogue")
    total = assessed = demonstrated = 0.0
    for weight, fraction in requirements:
        weight = number(weight, "requirement_weight")
        total += weight
        if fraction is not None:
            fraction = number(fraction, "demonstrated_fraction", high=1)
            assessed += weight
            demonstrated += weight * fraction
    if not math.isfinite(total) or total <= 0:
        raise ValueError("invalid_requirement_catalogue: positive total weight required")
    return (demonstrated / assessed if assessed else None, assessed / total)


def time_feasibility(hours_per_week, effort_hours, horizon_weeks=12):
    # Validate known inputs even when another input is unknown.
    for value, name in [(hours_per_week, "hours_per_week"),
                        (effort_hours, "effort_hours"), (horizon_weeks, "horizon_weeks")]:
        if value is not None:
            number(value, name)
    if horizon_weeks is not None and horizon_weeks <= 0:
        raise ValueError("horizon_weeks must be positive")
    if effort_hours == 0:
        return 1.0
    if None in (hours_per_week, effort_hours, horizon_weeks):
        return None
    # Divide first to avoid overflowing an otherwise bounded ratio.
    return min(1.0, (hours_per_week / effort_hours) * horizon_weeks)


def build_features(requirements, interest_alignment, resource_feasibility,
                   work_style_alignment, hours_per_week, effort_hours,
                   horizon_weeks=12, effort_low_hours=None, effort_high_hours=None):
    coverage, q = skill_coverage(requirements)
    return FeatureSnapshot(coverage, interest_alignment,
                           time_feasibility(hours_per_week, effort_hours, horizon_weeks),
                           resource_feasibility, work_style_alignment, q,
                           preparation_horizon_weeks=horizon_weeks,
                           preparation_evidence=PreparationEvidence(
                               hours_per_week, effort_hours, effort_low_hours, effort_high_hours))


def feature_matrix(snapshots):
    return [snapshot.vector() for snapshot in snapshots]
