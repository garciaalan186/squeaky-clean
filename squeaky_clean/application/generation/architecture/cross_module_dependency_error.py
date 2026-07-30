"""CrossModuleDependencyError: raised before ICP fan-out on cross-module dep violations."""

from __future__ import annotations


class CrossModuleDependencyError(RuntimeError):
    """Raised when an ArchitectureSpec has cross-module dependency violations.

    Aborts the pipeline *before* ICPs would have been spawned, so the
    user sees a concrete list of broken ``depends`` entries up front.
    Carries the offending violation strings on ``violations``.
    """

    def __init__(self, violations: tuple[str, ...]) -> None:
        self.violations: tuple[str, ...] = violations
        modules = sorted({_extract_module(v) for v in violations})
        modules = [m for m in modules if m]
        summary = (
            f"{len(violations)} cross-module dependency "
            f"violation{'s' if len(violations) != 1 else ''} "
            f"across {len(modules)} module(s): {modules}"
        )
        super().__init__(summary)


def _extract_module(violation: str) -> str:
    """Pull the source module name out of a violation string. Best-effort."""
    marker = "module "
    if violation.startswith(marker):
        rest = violation[len(marker):]
        if rest.startswith("'") and "'" in rest[1:]:
            return rest[1:].split("'", 1)[0]
    return ""
