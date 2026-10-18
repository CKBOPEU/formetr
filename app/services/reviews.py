from dataclasses import dataclass
from app.calculations.trends import review_progress


@dataclass(frozen=True)
class ReviewProposal:
    decision: str
    reason: str
    calorie_change_percent: int
    requires_confirmation: bool


def build_review(weights: list[float], goal: str) -> ReviewProposal:
    decision, reason, percent = review_progress(weights, goal)
    return ReviewProposal(decision, reason, percent, decision == "propose")
