"""Tests for ArchitecturalTradeoffScorer (weighted MCDA with hard gates)."""

import pytest

from squeaky_clean.application.dtos.recovery.decomposition_option import (
    DecompositionOption,
)
from squeaky_clean.application.use_cases.recovery.architectural_tradeoff_scorer import (
    ArchitecturalTradeoffScorer,
)


def _opt(name: str, testability: int, feasible: bool = True) -> DecompositionOption:
    return DecompositionOption(
        name=name, scores={"testability": testability}, feasible=feasible,
    )


def test_higher_weighted_score_wins() -> None:
    outcome = ArchitecturalTradeoffScorer().rank(
        (_opt("a", 5), _opt("b", 1)), {"testability": 1.0},
    )
    assert outcome.winner == "a"
    assert outcome.ranked[0] == ("a", 5.0)
    assert outcome.margin == 4.0
    assert outcome.close is False


def test_infeasible_option_is_excluded_even_if_top_scoring() -> None:
    outcome = ArchitecturalTradeoffScorer().rank(
        (_opt("violates", 5, feasible=False), _opt("clean", 2)),
        {"testability": 1.0},
    )
    assert outcome.winner == "clean"
    assert [name for name, _ in outcome.ranked] == ["clean"]


def test_small_margin_is_flagged_close() -> None:
    outcome = ArchitecturalTradeoffScorer().rank(
        (_opt("a", 5), _opt("b", 1)), {"testability": 0.1},
    )
    assert outcome.margin == pytest.approx(0.4)
    assert outcome.close is True


def test_no_feasible_options_raises() -> None:
    with pytest.raises(ValueError):
        ArchitecturalTradeoffScorer().rank(
            (_opt("x", 5, feasible=False),), {"testability": 1.0},
        )
