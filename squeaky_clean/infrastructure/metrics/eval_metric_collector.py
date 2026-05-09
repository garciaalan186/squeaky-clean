"""EvalMetricCollector: in-memory MetricCollector implementation."""

from copy import deepcopy
from dataclasses import fields

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.domain.entities.metric import Metric
from squeaky_clean.domain.interfaces.metric_collector import MetricCollector


class EvalMetricCollector(MetricCollector):
    """Collects metrics into a mutable EvalMetrics and returns snapshots."""

    def __init__(self) -> None:
        self._metrics: EvalMetrics = EvalMetrics.empty()
        self._valid_fields: frozenset[str] = frozenset(
            f.name for f in fields(self._metrics)
        )

    def record(self, metric: Metric) -> None:
        """Set the named scalar field on the running EvalMetrics."""
        if metric.name not in self._valid_fields:
            raise KeyError(f"Unknown EvalMetrics field: {metric.name}")
        current: object = getattr(self._metrics, metric.name)
        if isinstance(current, bool) or not isinstance(current, (int, float)):
            raise TypeError(f"Field {metric.name} is not a scalar numeric")
        if isinstance(current, int):
            setattr(self._metrics, metric.name, int(metric.value))
        else:
            setattr(self._metrics, metric.name, float(metric.value))

    def snapshot(self) -> EvalMetrics:
        """Return a deep copy of the current EvalMetrics state."""
        return deepcopy(self._metrics)
