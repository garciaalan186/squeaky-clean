"""CheckpointState: mutable checkpoint holder that persists every update (G3)."""

from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_writer import CheckpointWriter
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint


class CheckpointState:
    """Holds the current ``RunCheckpoint`` and writes a snapshot on every change."""

    def __init__(self, initial: RunCheckpoint, run_dir: Path) -> None:
        self._state: RunCheckpoint = initial
        self._run_dir: Path = run_dir
        self._writer: CheckpointWriter = CheckpointWriter()
        self._writer.write(self._state, self._run_dir)

    def update(self, **fields: object) -> None:
        """Apply ``fields`` to the checkpoint and persist the new snapshot."""
        self._state = replace(self._state, **fields)  # type: ignore[arg-type]
        self._writer.write(self._state, self._run_dir)
