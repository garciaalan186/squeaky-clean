"""Tests for RunEvalVelocity: tokens-per-second derivation and zero guards."""

import pytest

from squeaky_clean.application.evaluation.eval.run.run_eval_velocity import RunEvalVelocity
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics


def test_apply_computes_aggregate_and_per_agent_velocities() -> None:
    m = EvalMetrics.empty()
    m.total_wall_clock_ms = 2000
    m.total_tokens_output = 500
    m.artifact_token_estimate = 1000
    m.architect_output_tokens = 100
    m.architect_duration_ms = 500
    m.icp_output_tokens = 300
    m.icp_duration_ms = 1500
    m.icp_wall_duration_ms = 750
    RunEvalVelocity().apply(m)
    assert m.output_token_velocity == pytest.approx(250.0)
    assert m.artifact_token_velocity == pytest.approx(500.0)
    assert m.architect_velocity == pytest.approx(200.0)
    assert m.icp_velocity == pytest.approx(200.0)
    # Throughput uses wall duration (parallel ICPs), not summed duration.
    assert m.icp_throughput_velocity == pytest.approx(400.0)


def test_apply_with_zero_wall_clock_leaves_aggregates_at_zero() -> None:
    """No division by zero: unset durations must yield 0.0 velocities."""
    m = EvalMetrics.empty()
    m.total_tokens_output = 500
    m.artifact_token_estimate = 1000
    RunEvalVelocity().apply(m)
    assert m.output_token_velocity == 0.0
    assert m.artifact_token_velocity == 0.0


def test_apply_with_zero_agent_duration_yields_zero_for_that_agent() -> None:
    m = EvalMetrics.empty()
    m.total_wall_clock_ms = 1000
    m.test_architect_output_tokens = 400
    m.test_architect_duration_ms = 0
    m.architect_output_tokens = 50
    m.architect_duration_ms = 1000
    RunEvalVelocity().apply(m)
    assert m.test_architect_velocity == 0.0
    assert m.architect_velocity == pytest.approx(50.0)
