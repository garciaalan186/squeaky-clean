"""Tests for RefactorDecider (preserve vs split under user priorities)."""

from squeaky_clean.application.use_cases.recovery.criteria_weighting import (
    CriteriaWeighting,
)
from squeaky_clean.application.use_cases.recovery.refactor_decider import RefactorDecider

_PURITY_FIRST = (
    "testability", "evolvability", "performance",
    "simplicity", "migration_safety", "delivery_speed",
)
_SPEED_FIRST = (
    "simplicity", "delivery_speed", "migration_safety",
    "performance", "evolvability", "testability",
)


def _decide(ranking: tuple[str, ...]) -> str:
    weights = CriteriaWeighting().from_ranking(ranking)
    return RefactorDecider().decide(weights).winner


def test_purity_priorities_recommend_split() -> None:
    assert _decide(_PURITY_FIRST) == "split"


def test_speed_and_risk_priorities_recommend_preserve() -> None:
    assert _decide(_SPEED_FIRST) == "preserve"


def test_outcome_ranks_both_options() -> None:
    weights = CriteriaWeighting().from_ranking(_PURITY_FIRST)
    outcome = RefactorDecider().decide(weights)
    assert {name for name, _ in outcome.ranked} == {"preserve", "split"}
