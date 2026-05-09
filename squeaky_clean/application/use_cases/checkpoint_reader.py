"""CheckpointReader: load and validate a CHECKPOINT.json (G3 resumable runs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_CHECKPOINT_FILENAME = "CHECKPOINT.json"


class CheckpointReader:
    """Read ``<run_dir>/CHECKPOINT.json`` if present and valid; else return None."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def read(
        self, run_dir: Path, expected_checksum: str | None = None,
    ) -> RunCheckpoint | None:
        """Return checkpoint when valid; mismatched checksum → warn + None."""
        target = run_dir / _CHECKPOINT_FILENAME
        if not target.exists():
            return None
        try:
            data: dict[str, Any] = json.loads(target.read_text())
            checkpoint = RunCheckpoint(**data)
        except (OSError, ValueError, TypeError) as exc:
            self._logger.event(
                "checkpoint_read_failed",
                run_dir=str(run_dir), error=str(exc),
            )
            return None
        if expected_checksum and checkpoint.checksum != expected_checksum:
            self._logger.event(
                "checkpoint_checksum_mismatch",
                run_dir=str(run_dir),
                stored=checkpoint.checksum, expected=expected_checksum,
            )
            return None
        return checkpoint
