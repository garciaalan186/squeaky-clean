"""SecurityReview DTO: all security concerns for one ModuleSpec."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.security_concern import SecurityConcern


@dataclass(frozen=True)
class SecurityReview:
    """Immutable collection of security concerns from the SecurityArchitect.

    `concerns` is a tuple of SecurityConcern records, one per identified
    vulnerability or recommended defensive test.
    """

    concerns: tuple[SecurityConcern, ...]
