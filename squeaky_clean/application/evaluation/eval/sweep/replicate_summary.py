"""ReplicateSummary DTO: mean/stddev across N replicate EvalMetrics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplicateSummary:
    """Aggregated stats over N replicate runs of one problem."""

    problem_id: str
    replicates: int
    tests_pass_mean: float
    tests_pass_stddev: float
    functional_pass_mean: float
    functional_pass_stddev: float
    security_pass_mean: float
    security_pass_stddev: float
    cost_usd_mean: float
    cost_usd_stddev: float
    wall_clock_ms_mean: float
    wall_clock_ms_stddev: float
    cache_hit_ratio: float
