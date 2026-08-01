"""RefactorCommands: violation triage + refactor-plan application flows."""

import sys
from pathlib import Path

from squeaky_clean.application.generation.recovery.decomposition.interactive_triage import (
    InteractiveTriage,
)
from squeaky_clean.application.generation.recovery.refactor.refactor_emitter import RefactorEmitter
from squeaky_clean.application.generation.recovery.refactor.refactor_plan_serializer import (
    RefactorPlanSerializer,
)
from squeaky_clean.application.generation.recovery.scoring.violation_report_deserializer import (
    ViolationReportDeserializer,
)
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation


class RefactorCommands:
    """Executes the --triage and --refactor recovery flows."""

    def triage(self, rec: RecoveryInvocation) -> int:
        """Interactively triage a violations.json into refactor_plan.json."""
        path = Path(str(rec.triage))
        report = ViolationReportDeserializer().deserialize(path.read_text())
        plan = InteractiveTriage().run(report, self._console_ask)
        out = path.with_name("refactor_plan.json")
        out.write_text(RefactorPlanSerializer().serialize(plan))
        print(f"[squeaky] triage complete: {len(plan.fix)} to fix, "
              f"{len(plan.ignore)} ignored -> {out}")
        return 0

    def refactor_emit(self, rec: RecoveryInvocation) -> int:
        """Apply a refactor plan to a recovered Squib and emit the result."""
        if rec.plan is None:
            print("[squeaky] --refactor requires --plan", file=sys.stderr)
            return 1
        out = Path(rec.refactor_out) if rec.refactor_out else Path("refactored.squib")
        emitter = RefactorEmitter(LocalFileSystem(), Path(rec.plan))
        summary = emitter.emit(Path(str(rec.refactor)), out)
        print(f"[squeaky] refactored {summary.classes_before} -> "
              f"{summary.classes_after} classes across {summary.modules} "
              f"modules -> {summary.out_path}")
        return 0

    def _console_ask(self, category: str, count: int) -> bool:
        prompt = f"[squeaky] address all {count} {category} violation(s)? [Y/n] "
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            return True
        return answer not in ("n", "no")
