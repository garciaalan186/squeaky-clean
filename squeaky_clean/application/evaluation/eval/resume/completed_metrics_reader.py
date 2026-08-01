"""CompletedMetricsReader: rebuild EvalMetrics from a prior eval_report.json."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome


def _nested(
    data: dict[str, object], group: str, key: str, default: float,
) -> float:
    """Read ``data[group][key]``; fall back to flat ``data[key]`` (schema v1)."""
    sub = data.get(group)
    value: object = sub.get(key) if isinstance(sub, dict) else None
    if value is None:
        value = data.get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return default


class CompletedMetricsReader:
    """Reads the headline metrics of a completed run's eval_report.json.

    Accepts both schema v2 (nested ``cost``/``test_outcome`` payloads)
    and legacy flat v1 reports; missing or null values fall back to the
    checkpointed cost and a 0.0 pass rate.
    """

    def read(self, path: Path | None, fallback_cost: float) -> EvalMetrics:
        """Return an EvalMetrics carrying the prior run's cost + pass rate."""
        cost_usd, tests_pass = fallback_cost, 0.0
        if path is not None:
            data = json.loads(path.read_text()).get("metrics", {})
            cost_usd = _nested(data, "cost", "estimated_cost_usd", fallback_cost)
            tests_pass = _nested(data, "test_outcome", "tests_pass", 0.0)
        return EvalMetrics(
            cost=CostBreakdown(estimated_cost_usd=cost_usd),
            test_outcome=TestOutcome(tests_pass=tests_pass),
        )
