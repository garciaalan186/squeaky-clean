"""Tests for CheckpointState: snapshot on construction and on update."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_state import CheckpointState
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint


def _read(run_dir: Path) -> dict[str, object]:
    data: dict[str, object] = json.loads((run_dir / "CHECKPOINT.json").read_text())
    return data


def test_initial_snapshot_written_on_construction(tmp_path: Path) -> None:
    CheckpointState(RunCheckpoint(stage="started", problem_id="P0"), tmp_path)
    data = _read(tmp_path)
    assert data["stage"] == "started"
    assert data["problem_id"] == "P0"


def test_update_replaces_fields_and_persists(tmp_path: Path) -> None:
    state = CheckpointState(RunCheckpoint(stage="started"), tmp_path)
    state.update(stage="architect_done", architecture_notation="MODULE X\n")
    data = _read(tmp_path)
    assert data["stage"] == "architect_done"
    assert data["architecture_notation"] == "MODULE X\n"
