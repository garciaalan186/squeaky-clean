"""SeriesStatistics: rolling mean and 2-sigma regression detection."""

from __future__ import annotations

import math


class SeriesStatistics:
    """Pure helpers for time-series rolling means and regression flags."""

    def rolling_mean(self, values: list[float], window: int = 5) -> list[float]:
        """Return per-position trailing mean over the last ``window`` values."""
        out: list[float] = []
        for i in range(len(values)):
            chunk = values[max(0, i - window + 1): i + 1]
            out.append(sum(chunk) / len(chunk) if chunk else 0.0)
        return out

    def two_sigma_drops(
        self, values: list[float], lookback: int = 10,
    ) -> list[int]:
        """Return positional indices where ``values[i]`` ≤ mean − 2σ.

        Mean and σ are computed over the last ``lookback`` values only.
        Returns an empty list when the series is too short or σ is zero.
        """
        if len(values) < 3:
            return []
        recent = values[-lookback:]
        mean = sum(recent) / len(recent)
        var = sum((v - mean) ** 2 for v in recent) / len(recent)
        sd = math.sqrt(var)
        if sd == 0:
            return []
        return [i for i, v in enumerate(values) if v <= mean - 2 * sd]
