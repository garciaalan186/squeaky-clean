"""CostGuardrail: aborts a run when accumulated cost exceeds a USD cap."""

from __future__ import annotations


class CostExceededError(RuntimeError):
    """Raised when cumulative cost passes the configured cap."""


class CostGuardrail:
    """Tracks running USD cost; raises CostExceededError when over cap."""

    def __init__(self, max_usd: float) -> None:
        self._cap: float = max_usd
        self._spent: float = 0.0

    def add(self, delta_usd: float) -> None:
        """Add `delta_usd` to spend and raise CostExceededError if over cap."""
        self._spent += max(delta_usd, 0.0)
        if self._cap > 0 and self._spent > self._cap:
            raise CostExceededError(
                f"cost cap ${self._cap:.2f} exceeded (spent ${self._spent:.2f})"
            )

    def spent(self) -> float:
        """Return cumulative spend in USD."""
        return self._spent

    def remaining(self) -> float:
        """Return cap minus spent; negative iff already over cap."""
        return self._cap - self._spent
