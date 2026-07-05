"""RefactorEmitter: apply a RefactorPlan to a Squib, emit refactored.squib."""

from pathlib import Path

from squeaky_clean.application.dtos.recovery.refactor_run_summary import (
    RefactorRunSummary,
)
from squeaky_clean.application.use_cases.recovery.refactor_phase import RefactorPhase
from squeaky_clean.application.use_cases.recovery.refactor_plan_deserializer import (
    RefactorPlanDeserializer,
)
from squeaky_clean.application.use_cases.recovery.squib_review_gate import SquibReviewGate


class RefactorEmitter:
    """Loads a faithful Squib + a RefactorPlan and emits the refactored Squib.

    Parses the recovered Squib, applies the accepted transforms via
    RefactorPhase, and writes the result — ready to feed the existing
    ``--squib-file`` regeneration path. Deterministic; no LLM. Closes the
    Recover -> Analyze -> Triage -> Refactor loop on disk.
    """

    def __init__(self) -> None:
        self._gate: SquibReviewGate = SquibReviewGate()
        self._plans: RefactorPlanDeserializer = RefactorPlanDeserializer()
        self._phase: RefactorPhase = RefactorPhase()

    def emit(
        self, squib_path: Path, plan_path: Path, out_path: Path,
    ) -> RefactorRunSummary:
        """Apply the plan to the Squib and write the refactored Squib."""
        spec = self._gate.load(squib_path)
        plan = self._plans.deserialize(plan_path.read_text())
        before = sum(len(m.classes) for m in spec.modules)
        refactored = self._phase.apply(spec, plan)
        self._gate.emit(refactored, out_path)
        return RefactorRunSummary(
            classes_before=before,
            classes_after=sum(len(m.classes) for m in refactored.modules),
            modules=len(refactored.modules), out_path=str(out_path),
        )
