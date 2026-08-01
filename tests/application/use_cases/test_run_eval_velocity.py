"""Tests for RunEvalVelocity: tokens-per-second derivation and zero guards."""

import pytest

from squeaky_clean.application.evaluation.eval.run.run_eval_velocity import RunEvalVelocity
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.domain.value_objects.metrics.velocity_stats import VelocityStats


def test_compute_derives_aggregate_and_per_agent_velocities() -> None:
    m = EvalMetrics(
        total_wall_clock_ms=2000,
        cost=CostBreakdown(
            total_tokens_output=500,
            architect_output_tokens=100, architect_duration_ms=500,
            icp_output_tokens=300, icp_duration_ms=1500,
            icp_wall_duration_ms=750,
        ),
        velocity=VelocityStats(artifact_token_estimate=1000),
    )
    v = RunEvalVelocity().compute(m)
    assert v.output_token_velocity == pytest.approx(250.0)
    assert v.artifact_token_velocity == pytest.approx(500.0)
    assert v.architect_velocity == pytest.approx(200.0)
    assert v.icp_velocity == pytest.approx(200.0)
    # Throughput uses wall duration (parallel ICPs), not summed duration.
    assert v.icp_throughput_velocity == pytest.approx(400.0)
    # The artifact estimate seed is preserved in the returned VO.
    assert v.artifact_token_estimate == 1000


def test_compute_with_zero_wall_clock_leaves_aggregates_at_zero() -> None:
    """No division by zero: unset durations must yield 0.0 velocities."""
    m = EvalMetrics(
        cost=CostBreakdown(total_tokens_output=500),
        velocity=VelocityStats(artifact_token_estimate=1000),
    )
    v = RunEvalVelocity().compute(m)
    assert v.output_token_velocity == 0.0
    assert v.artifact_token_velocity == 0.0


def test_compute_with_zero_agent_duration_yields_zero_for_that_agent() -> None:
    m = EvalMetrics(
        total_wall_clock_ms=1000,
        cost=CostBreakdown(
            test_architect_output_tokens=400, test_architect_duration_ms=0,
            architect_output_tokens=50, architect_duration_ms=1000,
        ),
    )
    v = RunEvalVelocity().compute(m)
    assert v.test_architect_velocity == 0.0
    assert v.architect_velocity == pytest.approx(50.0)
