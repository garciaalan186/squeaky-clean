"""Tests for EvalMetricCollector."""

import pytest

from squeaky_clean.domain.entities.metric import Metric
from squeaky_clean.infrastructure.metrics.eval_metric_collector import EvalMetricCollector


def test_record_updates_scalar_field() -> None:
    c = EvalMetricCollector()
    c.record(Metric(name="total_tokens_input", value=123))
    assert c.snapshot().total_tokens_input == 123


def test_record_rejects_unknown_field() -> None:
    c = EvalMetricCollector()
    with pytest.raises(KeyError):
        c.record(Metric(name="nope", value=1))


def test_record_rejects_list_field() -> None:
    c = EvalMetricCollector()
    with pytest.raises(TypeError):
        c.record(Metric(name="classes_per_module", value=1))


def test_snapshot_returns_independent_copy() -> None:
    c = EvalMetricCollector()
    c.record(Metric(name="agent_retries", value=2))
    snap = c.snapshot()
    c.record(Metric(name="agent_retries", value=99))
    assert snap.agent_retries == 2
