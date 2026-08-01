"""Tests for the MCDAScoreRow DTO."""

import pytest

from squeaky_clean.application.shared.mcda.mcda_score_row import MCDAScoreRow


def test_holds_scores_and_total() -> None:
    row = MCDAScoreRow(technology="s3", version_pin="boto3==1.40",
                       scores={"fit": 5, "cost": 3}, weighted_score=4.2)
    assert row.technology == "s3"
    assert row.weighted_score == 4.2


def test_is_frozen() -> None:
    row = MCDAScoreRow(technology="t", version_pin="v", scores={}, weighted_score=0.0)
    with pytest.raises(AttributeError):
        row.weighted_score = 1.0  # type: ignore[misc]
