"""ReplicateAggregator: turn N EvalMetrics into a single ReplicateSummary."""

from __future__ import annotations

import math
from collections.abc import Sequence

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.replicate_summary import ReplicateSummary


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _stddev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = _mean(values)
    var = sum((v - mu) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)


class ReplicateAggregator:
    """Reduces a list of per-replicate EvalMetrics into a ReplicateSummary."""

    def aggregate(
        self,
        problem_id: str,
        replicates: Sequence[EvalMetrics],
    ) -> ReplicateSummary:
        """Compute mean/stddev across the supplied replicate EvalMetrics."""
        if not replicates:
            return ReplicateSummary(
                problem_id=problem_id, replicates=0,
                tests_pass_mean=0.0, tests_pass_stddev=0.0,
                functional_pass_mean=0.0, functional_pass_stddev=0.0,
                security_pass_mean=0.0, security_pass_stddev=0.0,
                cost_usd_mean=0.0, cost_usd_stddev=0.0,
                wall_clock_ms_mean=0.0, wall_clock_ms_stddev=0.0,
                cache_hit_ratio=0.0,
            )
        tp = [r.tests_pass for r in replicates]
        fp = [r.functional_tests_pass for r in replicates]
        sp = [r.security_tests_pass for r in replicates]
        cu = [r.estimated_cost_usd for r in replicates]
        wc = [float(r.total_wall_clock_ms) for r in replicates]
        hits = sum(r.cache_hit_count for r in replicates)
        total = sum(r.cache_hit_count + r.cache_miss_count for r in replicates)
        ratio = (hits / total) if total > 0 else 0.0
        return ReplicateSummary(
            problem_id=problem_id, replicates=len(replicates),
            tests_pass_mean=_mean(tp), tests_pass_stddev=_stddev(tp),
            functional_pass_mean=_mean(fp), functional_pass_stddev=_stddev(fp),
            security_pass_mean=_mean(sp), security_pass_stddev=_stddev(sp),
            cost_usd_mean=_mean(cu), cost_usd_stddev=_stddev(cu),
            wall_clock_ms_mean=_mean(wc), wall_clock_ms_stddev=_stddev(wc),
            cache_hit_ratio=ratio,
        )
