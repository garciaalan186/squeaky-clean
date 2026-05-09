"""CheckpointEmitter: persists per-stage checkpoints during pipeline runs (G3)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.use_cases.checkpoint_checksum import CheckpointChecksum
from squeaky_clean.application.use_cases.checkpoint_writer import CheckpointWriter
from squeaky_clean.application.use_cases.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.application.use_cases.test_architecture_serializer import (
    TestArchitectureSerializer,
)


class CheckpointEmitter:
    """Write per-stage checkpoint snapshots inside ``run_dir``."""

    def __init__(self, problem_id: str, run_dir: Path) -> None:
        self._run_dir: Path = run_dir
        self._writer: CheckpointWriter = CheckpointWriter()
        self._impls_ser = ModuleImplementationSerializer()
        self._test_ser = TestArchitectureSerializer()
        checksum = CheckpointChecksum().compute(problem_id)
        self._state: RunCheckpoint = RunCheckpoint(
            run_dir=str(run_dir), problem_id=problem_id,
            stage="started", checksum=checksum,
        )
        self._emit()

    def architect_done(self, notation: str) -> None:
        self._update(stage="architect_done", architecture_notation=notation)

    def test_arch_done(
        self, test_arch: TestArchitecture, sec_arch: TestArchitecture,
    ) -> None:
        ta = self._run_dir / "_resume_test_arch.json"
        sa = self._run_dir / "_resume_security_test_arch.json"
        self._safe_write(ta, self._test_ser.serialize(test_arch))
        self._safe_write(sa, self._test_ser.serialize(sec_arch))
        self._update(stage="test_arch_done", test_architecture_path=str(ta),
                     security_test_architecture_path=str(sa))

    def icps_done(self, impls: tuple[ModuleImplementation, ...]) -> None:
        path = self._run_dir / "_resume_module_impls.json"
        self._safe_write(path, self._impls_ser.serialize(impls))
        self._update(stage="icps_done", module_implementations_path=str(path))

    def integrated(self) -> None:
        self._update(stage="integrated", integration_done=True)

    def tested(self) -> None:
        self._update(stage="tested")

    def fixed(self, passes: int) -> None:
        self._update(stage="fixed", fixer_passes_completed=passes)

    def complete(self, cost_spent_usd: float) -> None:
        self._update(stage="complete", cost_spent_usd=cost_spent_usd)

    def _update(self, **fields: object) -> None:
        self._state = replace(self._state, **fields)  # type: ignore[arg-type]
        self._emit()

    def _emit(self) -> None:
        self._writer.write(self._state, self._run_dir)

    def _safe_write(self, path: Path, payload: str) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload)
        except OSError:
            pass
