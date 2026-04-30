"""CacheSummaryRenderer: render the SUMMARY.md ## Cache section."""

from __future__ import annotations

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics

_TIERS: tuple[str, ...] = ("architect", "manager", "icp", "fixer")


class CacheSummaryRenderer:
    """Render the prompt-cache breakdown as a Markdown table."""

    def render(self, m: EvalMetrics) -> list[str]:
        """Return the lines of the ## Cache section (with trailing blank)."""
        lines: list[str] = ["## Cache", ""]
        if not self._has_activity(m):
            lines.append("_No prompt-cache activity recorded._")
            lines.append("")
            return lines
        lines.append(
            "| Tier      | Cache create toks | Cache read toks "
            "| Hit ratio | Savings |"
        )
        lines.append(
            "|-----------|------------------:|----------------:"
            "|----------:|--------:|"
        )
        total_c, total_r = 0, 0
        for tier in _TIERS:
            c = int(getattr(m, f"cache_create_{tier}_tokens"))
            r = int(getattr(m, f"cache_read_{tier}_tokens"))
            ratio = float(getattr(m, f"cache_hit_ratio_{tier}"))
            s = float(getattr(m, f"cache_savings_{tier}_usd"))
            ratio_text = f"{ratio * 100:.1f}%" if (c + r) > 0 else "n/a"
            lines.append(
                f"| {tier.capitalize():<9} | {c:>17,} | {r:>15,} "
                f"| {ratio_text:>9} | ${s:.3f} |"
            )
            total_c += c
            total_r += r
        total_ratio = (
            f"{(total_r / (total_c + total_r) * 100):.1f}%"
            if (total_c + total_r) > 0 else "n/a"
        )
        lines.append(
            f"| **Total** | {total_c:>17,} | {total_r:>15,} "
            f"| {total_ratio:>9} | ${m.cache_savings_usd:.3f} |"
        )
        lines.append("")
        return lines

    def _has_activity(self, m: EvalMetrics) -> bool:
        return (
            m.cache_creation_input_tokens + m.cache_read_input_tokens
        ) > 0
