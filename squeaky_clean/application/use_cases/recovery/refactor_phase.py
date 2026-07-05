"""RefactorPhase: apply accepted transforms to the faithful spec."""

from squeaky_clean.application.dtos.recovery.refactor_plan import RefactorPlan
from squeaky_clean.application.use_cases.recovery.framework_coupling_transform import (
    FrameworkCouplingTransform,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_COUPLING_PREFIX = "framework-coupling:"


class RefactorPhase:
    """Fourth pipeline phase: apply transforms for fix-selected violations.

    v1 handles the framework-coupling category: every coupled class the
    triage kept in the plan's ``fix`` set is split into Entity + Repository
    + Adapter. Violations the reviewer ignored, and categories without a
    transform yet, are left untouched — the faithful spec is only changed
    where the human asked. Other categories are follow-up work.
    """

    def __init__(self) -> None:
        self._coupling: FrameworkCouplingTransform = FrameworkCouplingTransform()

    def apply(self, spec: ArchitectureSpec, plan: RefactorPlan) -> ArchitectureSpec:
        """Return the spec with accepted framework-coupling splits applied."""
        targets = frozenset(
            vid[len(_COUPLING_PREFIX):].rsplit(".", 1)[-1]
            for vid in plan.fix if vid.startswith(_COUPLING_PREFIX)
        )
        if not targets:
            return spec
        return self._coupling.apply(spec, targets)
