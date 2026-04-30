"""DashboardSeriesBuilder: turn snapshots into per-metric labelled series."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from squeaky_clean.application.dtos.run_metrics_snapshot import RunMetricsSnapshot
from squeaky_clean.application.use_cases.series_statistics import SeriesStatistics

_METRIC_KEYS: tuple[str, ...] = (
    "tests_pass", "estimated_cost_usd", "total_wall_clock_ms",
    "architecture_violations", "agent_retries",
    "cross_module_dependency_violations",
    "secret_leaks_detected", "sast_high_findings",
)


@dataclass(frozen=True)
class MetricSeries:
    """Per-metric values, rolling mean, and flagged-regression run numbers."""

    name: str
    labels: tuple[str, ...]
    values: tuple[float, ...]
    rolling_mean: tuple[float, ...]
    regressions: tuple[int, ...]


class DashboardSeriesBuilder:
    """Compute per-metric series, rolling means, and 2-sigma drops."""

    def build(
        self, snapshots: tuple[RunMetricsSnapshot, ...],
    ) -> tuple[MetricSeries, ...]:
        """Return one MetricSeries for every standard key plus cache_hit_ratio."""
        out: list[MetricSeries] = []
        for key in _METRIC_KEYS:
            out.append(self._series(key, snapshots, self._make_scalar(key)))
        out.append(self._series("cache_hit_ratio", snapshots, self._cache_ratio))
        return tuple(out)

    def _make_scalar(
        self, key: str,
    ) -> Callable[[RunMetricsSnapshot], float | None]:
        def extract(snap: RunMetricsSnapshot) -> float | None:
            raw = snap.metrics.get(key)
            return float(raw) if raw is not None else None
        return extract

    def _series(
        self, name: str, snapshots: tuple[RunMetricsSnapshot, ...],
        extractor: Callable[[RunMetricsSnapshot], float | None],
    ) -> MetricSeries:
        labels: list[str] = []
        values: list[float] = []
        runs: list[int] = []
        for snap in snapshots:
            raw = extractor(snap)
            if raw is None:
                continue
            labels.append(str(snap.run_number))
            values.append(raw)
            runs.append(snap.run_number)
        stats = SeriesStatistics()
        rolling = stats.rolling_mean(values)
        flagged_idx = stats.two_sigma_drops(values)
        return MetricSeries(
            name=name, labels=tuple(labels), values=tuple(values),
            rolling_mean=tuple(rolling),
            regressions=tuple(runs[i] for i in flagged_idx),
        )

    def _cache_ratio(self, snap: RunMetricsSnapshot) -> float | None:
        hit = snap.metrics.get("cache_hit_count")
        miss = snap.metrics.get("cache_miss_count")
        if hit is None or miss is None or (hit + miss) == 0:
            return None
        return float(hit) / float(hit + miss)
