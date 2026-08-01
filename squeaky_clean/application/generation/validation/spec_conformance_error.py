"""SpecConformanceError: architecture breaks the ProblemSpec semantic contract."""

from __future__ import annotations


class SpecConformanceError(ValueError):
    """Raised when an architecture violates the ProblemSpec semantic contract."""
