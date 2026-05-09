"""RunCheckpoint DTO: restartable pipeline state for resumable runs (G3)."""

from dataclasses import dataclass

_VALID_STAGES: frozenset[str] = frozenset({
    "started", "architect_done", "test_arch_done", "icps_done",
    "integrated", "tested", "fixed", "complete",
})
_SUPPORTED_VERSIONS: frozenset[str] = frozenset({"v1"})


@dataclass(frozen=True)
class RunCheckpoint:
    """Immutable snapshot of pipeline progress, written after each safe boundary.

    Holds enough state for ``ResumeRun`` to skip ahead to the next stage
    without re-invoking the architect or ICPs. ``checksum`` guards against
    schema drift across runs (different spec library hash → restart).
    """

    version: str = "v1"
    run_dir: str = ""
    problem_id: str = ""
    stage: str = ""
    architecture_notation: str = ""
    module_implementations_path: str = ""
    test_architecture_path: str = ""
    security_test_architecture_path: str = ""
    integration_done: bool = False
    fixer_passes_completed: int = 0
    cost_spent_usd: float = 0.0
    checksum: str = ""

    def __post_init__(self) -> None:
        """Validate version + stage; empty stage allowed (uninitialized)."""
        if self.version not in _SUPPORTED_VERSIONS:
            raise ValueError(
                f"unsupported checkpoint version {self.version!r}; "
                f"want one of {sorted(_SUPPORTED_VERSIONS)}"
            )
        if self.stage and self.stage not in _VALID_STAGES:
            raise ValueError(
                f"invalid stage {self.stage!r}; "
                f"want one of {sorted(_VALID_STAGES)}"
            )
