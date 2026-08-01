"""Tests for DecompositionOption: one candidate architectural choice for MCDA."""

import dataclasses

import pytest

from squeaky_clean.application.generation.recovery.refactor.decomposition_option import (
    DecompositionOption,
)


def test_defaults_mark_the_option_feasible_with_empty_description() -> None:
    option = DecompositionOption(name="preserve", scores={"simplicity": 5})
    assert option.feasible is True
    assert option.description == ""


def test_scores_map_each_criterion_to_its_rating() -> None:
    option = DecompositionOption(
        name="split", scores={"testability": 4, "simplicity": 2}, feasible=False,
    )
    assert option.scores["testability"] == 4
    assert option.feasible is False


def test_option_is_frozen() -> None:
    option = DecompositionOption(name="split", scores={})
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(option, "feasible", False)  # noqa: B010
