"""MetricCollector port: abstract interface for recording eval metrics."""

from abc import ABC, abstractmethod

from squeaky_clean.domain.entities.metric import Metric


class MetricCollector(ABC):
    """Port for recording named scalar metrics during a run.

    R6.3: ``snapshot`` returns the recorded name->value mapping. The old
    contract (mutating a named EvalMetrics field via ``setattr``) died
    with the frozen EvalMetrics; no production caller ever recorded
    through this port, so the honest surface is the plain mapping.
    """

    @abstractmethod
    def record(self, metric: Metric) -> None:
        """Record a single metric into the running totals."""

    @abstractmethod
    def snapshot(self) -> dict[str, float]:
        """Return a copy of the recorded metric values keyed by name."""
