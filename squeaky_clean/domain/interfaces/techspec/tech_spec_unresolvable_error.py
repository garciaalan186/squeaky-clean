"""TechSpecUnresolvableError: no source produced a valid TechSpec."""

from __future__ import annotations


class TechSpecUnresolvableError(RuntimeError):
    """Raised when no source can produce a valid TechSpec for the triple."""
