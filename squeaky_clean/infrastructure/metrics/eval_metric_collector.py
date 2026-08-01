"""EvalMetricCollector: in-memory MetricCollector implementation."""

from squeaky_clean.domain.entities.metric import Metric
from squeaky_clean.domain.interfaces.metric_collector import MetricCollector


class EvalMetricCollector(MetricCollector):
    """Collects named scalar metrics into a dict and returns copies.

    R6.3: replaces the ``setattr(metric.name)`` reflection over a mutable
    EvalMetrics with an explicit typed mapping.
    """

    def __init__(self) -> None:
        self._values: dict[str, float] = {}

    def record(self, metric: Metric) -> None:
        """Store the metric's value under its name (last write wins)."""
        self._values[metric.name] = float(metric.value)

    def snapshot(self) -> dict[str, float]:
        """Return a copy of the current recorded values."""
        return dict(self._values)
