"""CheckpointEmitter: persists per-stage checkpoints during pipeline runs (G3)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_checksum import CheckpointChecksum
from squeaky_clean.application.evaluation.eval.resume.checkpoint_progress import CheckpointProgress
from squeaky_clean.application.evaluation.eval.resume.checkpoint_state import CheckpointState
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.notation.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_serializer import (
    TestArchitectureSerializer,
)
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger


class CheckpointEmitter:
    """Write per-stage checkpoint snapshots inside ``run_dir``."""

    def __init__(
        self, problem_id: str, run_dir: Path, *, logger: RunLogger | None = None,
    ) -> None:
        self._run_dir, self._log = run_dir, logger or NullRunLogger()
        self._impls_ser = ModuleImplementationSerializer()
        self._test_ser: TestArchitectureSerializer = TestArchitectureSerializer()
        initial = RunCheckpoint(
            run_dir=str(run_dir), problem_id=problem_id, stage="started",
            checksum=CheckpointChecksum().compute(problem_id),
        )
        self._state: CheckpointState = CheckpointState(initial, run_dir)

    @property
    def progress(self) -> CheckpointProgress:
        """Markers for the payload-light stages (integrated/tested/fixed/complete)."""
        return CheckpointProgress(self._state)

    def architect_done(self, notation: str) -> None:
        self._state.update(stage="architect_done", architecture_notation=notation)

    def test_arch_done(
        self, test_arch: TestArchitecture, sec_arch: TestArchitecture,
    ) -> None:
        ta = self._run_dir / "_resume_test_arch.json"
        sa = self._run_dir / "_resume_security_test_arch.json"
        self._safe_write(ta, self._test_ser.serialize(test_arch))
        self._safe_write(sa, self._test_ser.serialize(sec_arch))
        self._state.update(stage="test_arch_done", test_architecture_path=str(ta),
                           security_test_architecture_path=str(sa))

    def icps_done(self, impls: tuple[ModuleImplementation, ...]) -> None:
        path = self._run_dir / "_resume_module_impls.json"
        self._safe_write(path, self._impls_ser.serialize(impls))
        self._state.update(stage="icps_done", module_implementations_path=str(path))

    def _safe_write(self, path: Path, payload: str) -> None:
        try:
            atomic_write_text(path, payload)
        except OSError as exc:  # best-effort resume artifact: log, never die
            self._log.event("checkpoint_artifact_write_failed",
                            path=str(path), error=str(exc))
