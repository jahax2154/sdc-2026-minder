"""Fixed-scale scores: never candidate-list normalization or probabilities."""

from .schemas import FEATURE_NAMES, TOLERANCE, number

BASELINE_WEIGHTS = (0.40, 0.20, 0.20, 0.10, 0.10)


def validate_weights(weights):
    if len(weights) != len(FEATURE_NAMES):
        raise ValueError("exactly five weights required")
    values = [number(w, "weight", high=1) for w in weights]
    if abs(sum(values) - 1) > TOLERANCE:
        raise ValueError("weights must sum to 1 within 1e-9; no normalization")
    return values


def baseline(snapshot, weights=BASELINE_WEIGHTS):
    return min(100.0, 100 * sum(w * x for w, x in
                              zip(validate_weights(weights), snapshot.vector())))


def learned_score(raw_grade):
    # A learned regressor may produce any finite real number.
    import math
    if isinstance(raw_grade, bool) or not isinstance(raw_grade, (int, float)) or not math.isfinite(raw_grade):
        raise ValueError("raw prediction must be finite")
    return 100 * min(1.0, max(0.0, raw_grade / 2))


def combine(personal_fit, market_index, fit_weight=0.7):
    f = number(personal_fit, "personal_fit", high=100)
    d = number(market_index, "market_index", high=100)
    weight = number(fit_weight, "fit_weight", high=1)
    return weight * f + (1 - weight) * d
