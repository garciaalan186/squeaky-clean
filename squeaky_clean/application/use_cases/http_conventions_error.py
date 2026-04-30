"""HttpConventionsError: raised on persistent constraint #22 violations."""

from __future__ import annotations


class HttpConventionsError(Exception):
    """Raised when an ArchitectureSpec violates HTTP-type convention rules."""

    def __init__(self, violations: tuple[str, ...]) -> None:
        super().__init__(
            f"{len(violations)} HTTP convention violations: {list(violations)}"
        )
        self.violations: tuple[str, ...] = violations
