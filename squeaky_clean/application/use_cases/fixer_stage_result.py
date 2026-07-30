"""FixerStageResult: aggregated outcome of one or more fixer-stage runs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FixerStageResult:
    """Aggregated outcome of one (or many) fixer-stage invocation(s)."""

    classes_fixed: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    passes: int = 0

    def merge(self, other: "FixerStageResult") -> "FixerStageResult":
        """Sum two FixerStageResults; use for multi-pass aggregation."""
        return FixerStageResult(
            classes_fixed=self.classes_fixed + other.classes_fixed,
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            duration_ms=self.duration_ms + other.duration_ms,
            passes=self.passes + other.passes,
        )
