"""TechSpecComposerError: raised when the composer cannot reconcile a spec."""

from __future__ import annotations


class TechSpecComposerError(Exception):
    """Raised when validation fails AND the Manager fallback cannot fix it.

    Carries both the validation errors and the Manager-proposed correction
    (if any) so a human operator can inspect the broken state. The
    composer raises this only after exhausting the validation -> Manager
    -> re-validate loop a single time.
    """

    def __init__(
        self,
        validation_errors: tuple[str, ...],
        proposed_spec: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            f"TechSpecComposer could not reconcile spec: {validation_errors}"
        )
        self.validation_errors: tuple[str, ...] = validation_errors
        self.proposed_spec: dict[str, object] | None = proposed_spec
