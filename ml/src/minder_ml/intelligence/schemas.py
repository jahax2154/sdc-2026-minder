"""Shared, versioned value objects; executable JSON schemas live in contracts/."""

from dataclasses import asdict, dataclass
from typing import Dict, List, Literal, Optional
import math

FEATURE_NAMES = (
    "skill_coverage", "interest_alignment", "time_feasibility",
    "resource_feasibility", "work_style_alignment",
)
FEATURE_VERSION = "personal-preparation-features-v1"
RUBRIC_VERSION = "personal-preparation-grades-v1"
SCORE_VERSION = "grade-to-index-v1"
RANKING_VERSION = "personal-fit-role-id-v1"
RESULT_VERSION = "minder-recommendation-v1"
TOLERANCE = 1e-9
ScorerKind = Literal["baseline", "ridge", "xgboost"]


def number(value, name, low=0.0, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value) or value < low or (high is not None and value > high):
        raise ValueError(f"{name} outside valid range")
    return value


def nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty")
    return value


@dataclass(frozen=True)
class PreparationEvidence:
    hours_per_week: Optional[float]
    effort_hours_used: Optional[float]
    effort_low_hours: Optional[float] = None
    effort_high_hours: Optional[float] = None

    def __post_init__(self):
        for name in ("hours_per_week", "effort_hours_used", "effort_low_hours", "effort_high_hours"):
            value = getattr(self, name)
            if value is not None:
                number(value, name)
        low, high, used = self.effort_low_hours, self.effort_high_hours, self.effort_hours_used
        if low is not None and high is not None and low > high:
            raise ValueError("effort range is reversed")
        if used is not None and ((low is not None and used < low) or (high is not None and used > high)):
            raise ValueError("selected effort outside reviewed range")


@dataclass(frozen=True)
class FeatureSnapshot:
    skill_coverage: Optional[float]
    interest_alignment: Optional[float]
    time_feasibility: Optional[float]
    resource_feasibility: Optional[float]
    work_style_alignment: Optional[float]
    assessed_requirement_fraction: float
    feature_schema_version: str = FEATURE_VERSION
    preparation_horizon_weeks: float = 12
    preparation_evidence: Optional[PreparationEvidence] = None

    def __post_init__(self):
        if self.feature_schema_version != FEATURE_VERSION:
            raise ValueError("incompatible feature schema")
        number(self.preparation_horizon_weeks, "preparation_horizon_weeks")
        if self.preparation_horizon_weeks <= 0:
            raise ValueError("positive preparation horizon required")
        for name in FEATURE_NAMES:
            value = getattr(self, name)
            if value is not None:
                number(value, name, high=1)
        number(self.assessed_requirement_fraction, "assessed_requirement_fraction", high=1)
        if self.assessed_requirement_fraction == 0 and self.skill_coverage is not None:
            raise ValueError("zero assessed weight requires unknown skill coverage")
        if self.assessed_requirement_fraction > 0 and self.skill_coverage is None:
            raise ValueError("assessed positive weight requires observed skill coverage")
        if self.preparation_evidence is not None:
            from .features import time_feasibility
            evidence = self.preparation_evidence
            expected = time_feasibility(evidence.hours_per_week, evidence.effort_hours_used,
                                        self.preparation_horizon_weeks)
            if (expected is None) != (self.time_feasibility is None) or (
                expected is not None and abs(expected - self.time_feasibility) > TOLERANCE
            ):
                raise ValueError("time snapshot disagrees with recorded preparation evidence")

    @property
    def eligible(self):
        return (abs(self.assessed_requirement_fraction - 1) <= TOLERANCE
                and all(getattr(self, n) is not None for n in FEATURE_NAMES))

    def vector(self):
        if not self.eligible:
            raise ValueError("insufficient_information: complete features and Q=1 required")
        return [float(getattr(self, name)) for name in FEATURE_NAMES]

    def components(self):
        return {name: getattr(self, name) for name in FEATURE_NAMES}

    @classmethod
    def from_dict(cls, row):
        # Deliberate allowlist: targets, IDs, market and provenance never enter X.
        return cls(**{n: row.get(n) for n in FEATURE_NAMES},
                   assessed_requirement_fraction=row["assessed_requirement_fraction"],
                   feature_schema_version=row["feature_schema_version"],
                   preparation_horizon_weeks=row["preparation_horizon_weeks"],
                   preparation_evidence=PreparationEvidence(**row["preparation_evidence"])
                   if row.get("preparation_evidence") is not None else None)


@dataclass(frozen=True)
class RoleInput:
    role_id: str
    features: FeatureSnapshot
    evidence_ids: List[str]

    def __post_init__(self):
        nonempty(self.role_id, "role_id")
        for value in self.evidence_ids:
            nonempty(value, "evidence_id")


@dataclass
class RoleResult:
    role_id: str
    personal_fit_index: Optional[float]
    market_assessment_index: Optional[float]
    overall_match_index: Optional[float]
    evidence_coverage: float
    feature_components: Dict[str, Optional[float]]
    evidence_ids: List[str]
    raw_grade_prediction: Optional[float]
    preparation_evidence: Optional[Dict]
    reason: Optional[str] = None


@dataclass
class RecommendationResult:
    result_schema_version: str
    profile_version: str
    feature_schema_version: str
    scorer_kind: ScorerKind
    model_version: Optional[str]
    score_mapping_version: str
    ranking_policy_version: str
    evidence_snapshot_id: str
    role_catalogue_version: str
    ranking_mode: str
    fit_weight: float
    preparation_horizon_weeks: float
    result_kind: str
    options: List[RoleResult]
    unscored_roles: List[RoleResult]
    warnings: List[str]

    def to_dict(self):
        return asdict(self)
