"""PercentileSummaryRenderer: per-tier latency + cost percentiles for SUMMARY.md."""

from __future__ import annotations

from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder

_TIERS: tuple[str, ...] = ("architect", "manager", "icp", "fixer")


class PercentileSummaryRenderer:
    """Renders a per-tier latency + cost percentile table for SUMMARY.md."""

    def render(self, recorder: LLMUsageRecorder) -> str:
        """Return a markdown section with p50/p95 latency + p50/p95 cost per tier."""
        rows: list[str] = []
        any_data = False
        for tier in _TIERS:
            durations, costs = recorder.tier_samples(tier)
            if not durations:
                rows.append(
                    f"| {tier.title():9s} | n/a | n/a | n/a | n/a | 0 |"
                )
                continue
            any_data = True
            p50_lat = self._percentile(durations, 0.50)
            p95_lat = self._percentile(durations, 0.95)
            p50_cost = self._percentile(costs, 0.50)
            p95_cost = self._percentile(costs, 0.95)
            rows.append(
                f"| {tier.title():9s} | {int(p50_lat):>5d}ms | "
                f"{int(p95_lat):>5d}ms | ${p50_cost:.4f} | "
                f"${p95_cost:.4f} | {len(durations)} |"
            )
        if not any_data:
            return ""
        return (
            "## Latency / cost percentiles\n\n"
            "| Tier      | p50 lat | p95 lat | p50 cost | p95 cost | n |\n"
            "|-----------|--------:|--------:|---------:|---------:|--:|\n"
            + "\n".join(rows)
            + "\n"
        )

    @staticmethod
    def _percentile(samples: tuple[float, ...] | tuple[int, ...], q: float) -> float:
        if not samples:
            return 0.0
        sorted_s = sorted(samples)
        idx = min(int(q * (len(sorted_s) - 1)), len(sorted_s) - 1)
        return float(sorted_s[idx])
