"""Tests for MCDAWeights (H3)."""

import pytest

from squeaky_clean.application.dtos.mcda_weights import MCDAWeights


def test_default_weights_sum_to_one() -> None:
    w = MCDAWeights()
    assert sum(w.as_dict().values()) == pytest.approx(1.0)


def test_rejects_weights_not_summing_to_one() -> None:
    with pytest.raises(ValueError, match="must sum to 1.0"):
        MCDAWeights(ops=0.5)


def test_from_mapping_round_trips() -> None:
    src = {"ops": 0.20, "cost": 0.20, "cold": 0.10, "thru": 0.15,
           "eco": 0.10, "reg": 0.05, "lic": 0.05, "team": 0.15}
    w = MCDAWeights.from_mapping(src)
    assert w.as_dict() == src


def test_from_mapping_rejects_unknown_key() -> None:
    with pytest.raises(ValueError, match="unknown MCDA criterion"):
        MCDAWeights.from_mapping({"bogus": 1.0})
