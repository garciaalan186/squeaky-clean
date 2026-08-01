"""Tests for the VelocityStats value object."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.velocity_stats import VelocityStats


def test_defaults_are_zero() -> None:
    v = VelocityStats()
    assert v.artifact_token_estimate == 0
    assert v.output_token_velocity == 0.0
    assert v.icp_throughput_velocity == 0.0


def test_is_frozen() -> None:
    v = VelocityStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.icp_velocity = 1.0  # type: ignore[misc]


def test_holds_derived_values() -> None:
    v = VelocityStats(
        artifact_token_estimate=400, artifact_to_output_ratio=0.5,
        architect_velocity=12.5,
    )
    assert v.artifact_token_estimate == 400
    assert v.artifact_to_output_ratio == pytest.approx(0.5)
    assert v.architect_velocity == pytest.approx(12.5)
