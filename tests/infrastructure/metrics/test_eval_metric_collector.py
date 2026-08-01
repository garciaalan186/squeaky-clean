"""Tests for EvalMetricCollector (dict-based, R6.3)."""

from squeaky_clean.domain.entities.metric import Metric
from squeaky_clean.infrastructure.metrics.eval_metric_collector import EvalMetricCollector


def test_record_stores_named_scalar() -> None:
    c = EvalMetricCollector()
    c.record(Metric(name="total_tokens_input", value=123))
    assert c.snapshot()["total_tokens_input"] == 123.0


def test_last_write_wins() -> None:
    c = EvalMetricCollector()
    c.record(Metric(name="agent_retries", value=1))
    c.record(Metric(name="agent_retries", value=3))
    assert c.snapshot()["agent_retries"] == 3.0


def test_snapshot_starts_empty() -> None:
    assert EvalMetricCollector().snapshot() == {}


def test_snapshot_returns_independent_copy() -> None:
    c = EvalMetricCollector()
    c.record(Metric(name="agent_retries", value=2))
    snap = c.snapshot()
    c.record(Metric(name="agent_retries", value=99))
    assert snap["agent_retries"] == 2.0
