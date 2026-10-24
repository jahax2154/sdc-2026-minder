"""Explanation boundary. No score, canonical URL or profile mutation authority."""

from dataclasses import dataclass
from typing import Dict, List, Literal, Protocol
from .schemas import RecommendationResult


@dataclass(frozen=True)
class ProposedChange:
    kind: Literal["set_weekly_hours", "set_interest", "set_work_preference"]
    field: str
    value: object
    reason: str


@dataclass(frozen=True)
class Explanation:
    status: Literal["disabled", "available"]
    text: str
    evidence_ids: List[str]
    proposed_changes: List[ProposedChange]


class ExplanationAdapter(Protocol):
    def explain(self, result: RecommendationResult, evidence: List[Dict]) -> Explanation:
        ...


class DisabledExplanationAdapter:
    def explain(self, result, evidence):
        return Explanation("disabled", "LLM explanation is disabled.", [], [])
