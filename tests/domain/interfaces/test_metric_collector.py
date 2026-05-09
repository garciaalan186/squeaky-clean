"""Tests for MetricCollector ABC."""

import pytest

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.domain.entities.metric import Metric
from squeaky_clean.domain.interfaces.metric_collector import MetricCollector


class _StubCollector(MetricCollector):
    def __init__(self) -> None:
        self._m = EvalMetrics.empty()

    def record(self, metric: Metric) -> None:
        self._m.total_tokens_input = int(metric.value)

    def snapshot(self) -> EvalMetrics:
        return self._m


def test_metric_collector_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        MetricCollector()  # type: ignore[abstract]


def test_stub_collector_records_and_snapshots() -> None:
    c = _StubCollector()
    c.record(Metric(name="total_tokens_input", value=42))
    assert c.snapshot().total_tokens_input == 42
