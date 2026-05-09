"""CheckpointWriter: atomic JSON checkpoint persistence (G3 resumable runs)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_CHECKPOINT_FILENAME = "CHECKPOINT.json"


class CheckpointWriter:
    """Write a RunCheckpoint to ``<run_dir>/CHECKPOINT.json`` atomically.

    Best-effort: any OSError is logged via JSONLogger but never raised;
    the pipeline must keep running even when checkpoint persistence
    fails (per G3 contract).
    """

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def write(self, checkpoint: RunCheckpoint, run_dir: Path) -> None:
        """Serialize ``checkpoint`` as JSON to ``<run_dir>/CHECKPOINT.json``."""
        target = run_dir / _CHECKPOINT_FILENAME
        tmp = target.with_suffix(".json.tmp")
        try:
            run_dir.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(asdict(checkpoint), indent=2, default=str)
            tmp.write_text(payload)
            os.replace(tmp, target)
        except OSError as exc:
            self._logger.event(
                "checkpoint_write_failed",
                run_dir=str(run_dir), stage=checkpoint.stage, error=str(exc),
            )
