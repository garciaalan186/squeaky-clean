"""CostGate: tracks running USD spend and gates future calls against a budget."""

from threading import Lock

from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.use_cases.budget_exceeded_error import (
    BudgetExceededError,
)

__all__ = ["BudgetExceededError", "CostGate"]


class CostGate:
    """Thread-safe per-run accumulator that enforces a CostBudget cap.

    Enforcement is PRE-FLIGHT via ``reserve``/``settle``: a caller reserves an
    estimated cost (atomically checked against the cap) BEFORE spending, then
    settles the actual cost afterward. This bounds parallel overshoot to the
    reservation estimate rather than letting racing threads each read a
    below-cap total and all proceed. ``check``/``record`` remain for callers
    that only need post-hoc accounting.
    """

    def __init__(self, budget: CostBudget | None = None) -> None:
        self._budget: CostBudget = budget or CostBudget()
        self._spent_usd: float = 0.0
        self._reserved_usd: float = 0.0
        self._warned: bool = False
        self._lock: Lock = Lock()

    def seed(self, prior_usd: float) -> None:
        """Seed cumulative spend (e.g. cost already spent before a resume)."""
        with self._lock:
            self._spent_usd += max(prior_usd, 0.0)

    def reserve(self, estimate_usd: float) -> float:
        """Atomically check+hold ``estimate_usd`` against the cap; raise if over."""
        est = max(estimate_usd, 0.0)
        with self._lock:
            cap = self._budget.max_cost_usd
            projected = self._spent_usd + self._reserved_usd + est
            if cap is not None and projected > cap:
                raise BudgetExceededError(
                    f"projected spend ${projected:.4f} exceeds cap ${cap:.4f}"
                )
            self._reserved_usd += est
        return est

    def settle(self, reserved_usd: float, actual_usd: float) -> None:
        """Release a reservation and record the actual spend; raise if now over."""
        with self._lock:
            self._reserved_usd = max(self._reserved_usd - reserved_usd, 0.0)
            self._spent_usd += max(actual_usd, 0.0)
            spent, cap = self._spent_usd, self._budget.max_cost_usd
            warn_at = self._budget.warn_threshold_usd()
            warn = warn_at is not None and not self._warned and spent >= warn_at
            if warn:
                self._warned = True
        if warn:
            print(f"[squeaky] WARN cost ${spent:.4f} >= "
                  f"{int(self._budget.warn_at_pct * 100)}% of cap ${cap:.4f}")
        if cap is not None and spent > cap:
            raise BudgetExceededError(f"spend ${spent:.4f} exceeded cap ${cap:.4f}")

    def check(self, additional_usd: float) -> None:
        """Raise BudgetExceededError if recording ``additional_usd`` would over-spend."""
        if self.would_exceed(additional_usd):
            with self._lock:
                projected = self._spent_usd + self._reserved_usd + max(
                    additional_usd, 0.0
                )
                cap = self._budget.max_cost_usd
            raise BudgetExceededError(
                f"projected spend ${projected:.4f} exceeds cap ${cap:.4f}"
            )

    def record(self, actual_usd: float) -> None:
        """Add ``actual_usd`` to the running total; raise if cap now exceeded."""
        self.settle(0.0, actual_usd)

    def would_exceed(self, additional_usd: float) -> bool:
        """Return True iff ``spent + reserved + additional`` would tip over the cap."""
        cap = self._budget.max_cost_usd
        if cap is None:
            return False
        with self._lock:
            return (
                self._spent_usd + self._reserved_usd + max(additional_usd, 0.0)
            ) > cap

    def spent_usd(self) -> float:
        """Return cumulative spend in USD."""
        with self._lock:
            return self._spent_usd

    def budget(self) -> CostBudget:
        """Return the configured CostBudget."""
        return self._budget
