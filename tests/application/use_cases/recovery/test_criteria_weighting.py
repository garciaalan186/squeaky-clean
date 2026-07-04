"""Tests for CriteriaWeighting (rank-order-centroid weights)."""

import pytest

from squeaky_clean.application.use_cases.recovery.criteria_weighting import (
    CriteriaWeighting,
)

_RANKING = ("testability", "evolvability", "simplicity")


def test_weights_sum_to_one() -> None:
    weights = CriteriaWeighting().from_ranking(_RANKING)
    assert abs(sum(weights.values()) - 1.0) < 1e-9


def test_weights_are_strictly_descending_by_rank() -> None:
    w = CriteriaWeighting().from_ranking(_RANKING)
    assert w["testability"] > w["evolvability"] > w["simplicity"]


def test_top_rank_dominates() -> None:
    w = CriteriaWeighting().from_ranking(_RANKING)
    # ROC for n=3: top = (1 + 1/2 + 1/3)/3 ~= 0.611
    assert w["testability"] == pytest.approx((1 + 0.5 + 1 / 3) / 3)


def test_unknown_criterion_rejected() -> None:
    with pytest.raises(ValueError):
        CriteriaWeighting().from_ranking(("testability", "bogus"))


def test_duplicate_criterion_rejected() -> None:
    with pytest.raises(ValueError):
        CriteriaWeighting().from_ranking(("testability", "testability"))


def test_empty_ranking_rejected() -> None:
    with pytest.raises(ValueError):
        CriteriaWeighting().from_ranking(())
