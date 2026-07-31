"""Tests for the ComplexityScore DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.complexity_score import ComplexityScore


def test_defaults_are_zero_except_normalized() -> None:
    score = ComplexityScore()
    assert score.structural == 0.0
    assert score.codegen == 0.0
    assert score.constraint == 0.0
    assert score.composite == 0.0
    assert score.normalized == 1.0
    assert score.components == {}


def test_is_frozen() -> None:
    score = ComplexityScore()
    with pytest.raises(dataclasses.FrozenInstanceError):
        score.composite = 2.0  # type: ignore[misc]


def test_components_default_factory_is_per_instance() -> None:
    a = ComplexityScore()
    b = ComplexityScore()
    assert a.components is not b.components


def test_stores_explicit_values() -> None:
    score = ComplexityScore(
        structural=1.0, codegen=2.0, constraint=3.0,
        composite=6.0, normalized=1.5, components={"S": 1.0},
    )
    assert score.composite == 6.0
    assert score.components == {"S": 1.0}
