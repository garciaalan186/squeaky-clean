"""GoldenMetrics VO: calibrated per-problem eval baselines (R5.2)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoldenMetrics:
    """Routing-stamped N>=3 baseline a problem's eval scores regress against.

    Self-contained by design: lives in shared/ (ProblemSpec's component), so
    it must NOT import evaluation/ types — the evaluation side converts this
    to its ReplicateSummary for detection. ``model_routing`` records the
    tier->model mapping the calibration ran under ("architect=...", ...);
    scores from a different routing are not comparable (model change, not
    framework regression) and must not gate.
    """

    replicates: int
    tests_pass_mean: float
    tests_pass_stddev: float
    functional_pass_mean: float
    functional_pass_stddev: float
    security_pass_mean: float
    security_pass_stddev: float
    cost_usd_mean: float
    cost_usd_stddev: float
    model_routing: tuple[str, ...] = field(default_factory=tuple)
    calibrated_run: str = ""

    def routing_matches(self, models: dict[str, str]) -> bool:
        """True when ``models`` (tier -> model) equals the calibration routing."""
        current = tuple(sorted(f"{t}={m}" for t, m in models.items()))
        return current == tuple(sorted(self.model_routing))
