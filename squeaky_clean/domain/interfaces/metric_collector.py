"""MetricCollector port: abstract interface for recording eval metrics."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from squeaky_clean.domain.entities.metric import Metric

if TYPE_CHECKING:
    from squeaky_clean.application.dtos.eval_metrics import EvalMetrics


class MetricCollector(ABC):
    """Port for recording metrics during a run and taking a final snapshot."""

    @abstractmethod
    def record(self, metric: Metric) -> None:
        """Record a single metric into the running totals."""

    @abstractmethod
    def snapshot(self) -> "EvalMetrics":
        """Return an immutable-at-call-time copy of current EvalMetrics."""
