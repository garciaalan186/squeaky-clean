"""Tests for CheckpointWriter (G3)."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.use_cases.checkpoint_writer import CheckpointWriter


def test_write_emits_atomic_json(tmp_path: Path) -> None:
    cp = RunCheckpoint(
        run_dir=str(tmp_path), problem_id="P0",
        stage="architect_done", architecture_notation="MODULE X\n",
        cost_spent_usd=0.5, checksum="abcd",
    )
    CheckpointWriter().write(cp, tmp_path)
    target = tmp_path / "CHECKPOINT.json"
    assert target.exists()
    data = json.loads(target.read_text())
    assert data["stage"] == "architect_done"
    assert data["problem_id"] == "P0"
    assert data["architecture_notation"] == "MODULE X\n"
    assert data["cost_spent_usd"] == 0.5


def test_write_failure_is_swallowed(tmp_path: Path) -> None:
    """A non-existent + read-only parent is best-effort: no exception raised."""
    cp = RunCheckpoint(stage="started")
    bad_dir = tmp_path / "blocked"
    bad_dir.touch()  # file, not a directory → mkdir raises FileExistsError
    CheckpointWriter().write(cp, bad_dir / "child")
    assert not (bad_dir / "child" / "CHECKPOINT.json").exists()
