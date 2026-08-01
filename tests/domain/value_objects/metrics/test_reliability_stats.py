"""Tests for the ReliabilityStats value object."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.metrics.reliability_stats import ReliabilityStats


def test_defaults_are_zero() -> None:
    r = ReliabilityStats()
    assert r.agent_retries == 0
    assert r.llm_timeouts == 0
    assert r.compile_errors == 0
    assert r.classes_fixed == 0
    assert r.fixer_cost_usd == 0.0


def test_is_frozen() -> None:
    r = ReliabilityStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.agent_retries = 1  # type: ignore[misc]


def test_holds_repair_telemetry() -> None:
    r = ReliabilityStats(
        agent_retries=2, agent_hangs=1, llm_timeouts=1,
        classes_fixed=3, fixer_input_tokens=500, fixer_cost_usd=0.02,
    )
    assert r.agent_hangs == 1
    assert r.classes_fixed == 3
    assert r.fixer_cost_usd == pytest.approx(0.02)
