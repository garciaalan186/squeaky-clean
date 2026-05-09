"""RegressionRecord DTO: one detected regression of a metric."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionRecord:
    """Stores one regression: metric, problem, baseline mean -> current mean."""

    metric: str
    problem_id: str
    baseline_mean: float
    baseline_stddev: float
    current_mean: float
    current_stddev: float
    sigma_drop: float
    timestamp: str
