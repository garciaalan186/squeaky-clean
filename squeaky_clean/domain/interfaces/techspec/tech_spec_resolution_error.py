"""TechSpecResolutionError: resolution failure carrying per-source reasons."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.techspec.tech_spec_unresolvable_error import (
    TechSpecUnresolvableError,
)


class TechSpecResolutionError(TechSpecUnresolvableError):
    """TechSpecUnresolvableError that carries per-source failure reasons (R6.8).

    Subclasses the port error so existing ``except TechSpecUnresolvableError``
    sites keep working, while callers (and the JSON event log) see WHY every
    source failed instead of a silent degrade.
    """

    def __init__(self, message: str, reasons: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.reasons: tuple[str, ...] = reasons
