"""Tests for CheckpointProgress: payload-light stage markers."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_progress import CheckpointProgress
from squeaky_clean.application.evaluation.eval.resume.checkpoint_state import CheckpointState
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint


def _read(run_dir: Path) -> dict[str, object]:
    data: dict[str, object] = json.loads((run_dir / "CHECKPOINT.json").read_text())
    return data


def test_markers_advance_stage_with_payload_fields(tmp_path: Path) -> None:
    progress = CheckpointProgress(
        CheckpointState(RunCheckpoint(stage="icps_done"), tmp_path)
    )
    progress.integrated()
    after = _read(tmp_path)
    assert after["stage"] == "integrated"
    assert after["integration_done"] is True
    progress.tested()
    assert _read(tmp_path)["stage"] == "tested"
    progress.fixed(3)
    after = _read(tmp_path)
    assert after["stage"] == "fixed"
    assert after["fixer_passes_completed"] == 3
    progress.complete(0.7)
    after = _read(tmp_path)
    assert after["stage"] == "complete"
    assert after["cost_spent_usd"] == 0.7
