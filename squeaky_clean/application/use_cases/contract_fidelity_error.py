"""ContractFidelityError: raised when a service fails its cross-service contracts."""

from __future__ import annotations


class ContractFidelityError(RuntimeError):
    """Raised when produces/consumes Contracts are violated by an architecture.

    Carries the offending violation strings on ``violations`` so the
    pipeline (and downstream tools) can surface them verbatim.
    """

    def __init__(self, violations: tuple[str, ...]) -> None:
        self.violations: tuple[str, ...] = violations
        n = len(violations)
        plural = "" if n == 1 else "s"
        super().__init__(
            f"{n} contract fidelity violation{plural}: {list(violations)}"
        )
