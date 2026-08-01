"""MetricSeries: one dashboard metric's labelled series + rolling stats."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSeries:
    """Per-metric values, rolling mean, and flagged-regression run numbers."""

    name: str
    labels: tuple[str, ...]
    values: tuple[float, ...]
    rolling_mean: tuple[float, ...]
    regressions: tuple[int, ...]
