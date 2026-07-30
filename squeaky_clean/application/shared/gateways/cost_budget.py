"""CostBudget DTO: per-run USD cap with warn-threshold."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CostBudget:
    """Immutable cost ceiling. ``max_cost_usd=None`` disables enforcement."""

    max_cost_usd: float | None = None
    warn_at_pct: float = 0.8

    def __post_init__(self) -> None:
        """Validate cap >= 0 (if set) and 0 < warn_at_pct <= 1."""
        if self.max_cost_usd is not None and self.max_cost_usd < 0:
            raise ValueError("max_cost_usd must be >= 0 or None")
        if not (0.0 < self.warn_at_pct <= 1.0):
            raise ValueError("warn_at_pct must be in (0, 1]")

    def is_unlimited(self) -> bool:
        """Return True iff no cap is configured."""
        return self.max_cost_usd is None

    def warn_threshold_usd(self) -> float | None:
        """Return USD threshold at which a warning should fire, or None."""
        if self.max_cost_usd is None:
            return None
        return self.max_cost_usd * self.warn_at_pct
