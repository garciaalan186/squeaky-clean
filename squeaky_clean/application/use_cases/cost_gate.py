"""CostGate: tracks running USD spend and gates future calls against a budget."""

from threading import Lock

from squeaky_clean.application.dtos.cost_budget import CostBudget


class BudgetExceededError(RuntimeError):
    """Raised when recording or projecting a spend would exceed the cap."""


class CostGate:
    """Mutable per-run accumulator that enforces a CostBudget cap."""

    def __init__(self, budget: CostBudget | None = None) -> None:
        self._budget: CostBudget = budget or CostBudget()
        self._spent_usd: float = 0.0
        self._warned: bool = False
        self._lock: Lock = Lock()

    def check(self, additional_usd: float) -> None:
        """Raise BudgetExceededError if recording ``additional_usd`` would over-spend."""
        if self.would_exceed(additional_usd):
            raise BudgetExceededError(
                f"projected spend ${self._spent_usd + additional_usd:.4f} "
                f"exceeds cap ${self._budget.max_cost_usd:.4f}"
            )

    def record(self, actual_usd: float) -> None:
        """Add ``actual_usd`` to the running total; raise if cap now exceeded."""
        with self._lock:
            self._spent_usd += max(actual_usd, 0.0)
            spent = self._spent_usd
        cap = self._budget.max_cost_usd
        warn_at = self._budget.warn_threshold_usd()
        if warn_at is not None and not self._warned and spent >= warn_at:
            self._warned = True
            print(f"[squeaky] WARN cost ${spent:.4f} >= "
                  f"{int(self._budget.warn_at_pct * 100)}% of cap ${cap:.4f}")
        if cap is not None and spent > cap:
            raise BudgetExceededError(
                f"spend ${spent:.4f} exceeded cap ${cap:.4f}"
            )

    def would_exceed(self, additional_usd: float) -> bool:
        """Return True iff ``spent + additional`` would tip over the cap."""
        cap = self._budget.max_cost_usd
        if cap is None:
            return False
        return (self._spent_usd + max(additional_usd, 0.0)) > cap

    def spent_usd(self) -> float:
        """Return cumulative spend in USD."""
        return self._spent_usd

    def budget(self) -> CostBudget:
        """Return the configured CostBudget."""
        return self._budget
