"""CostExceededError: cumulative run cost passed the configured cap."""

from __future__ import annotations


class CostExceededError(RuntimeError):
    """Raised when cumulative cost passes the configured cap."""
