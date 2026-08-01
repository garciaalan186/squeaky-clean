"""UnknownConventionError: unregistered domain-convention tag lookup."""

from __future__ import annotations


class UnknownConventionError(ValueError):
    """Raised when a convention tag has no registered expansion."""
