"""Tests for CheckpointReader (G3)."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.use_cases.checkpoint_reader import CheckpointReader
from squeaky_clean.application.use_cases.checkpoint_writer import CheckpointWriter


def test_read_returns_none_when_missing(tmp_path: Path) -> None:
    assert CheckpointReader().read(tmp_path) is None


def test_round_trip(tmp_path: Path) -> None:
    cp = RunCheckpoint(stage="icps_done", problem_id="P1", checksum="x")
    CheckpointWriter().write(cp, tmp_path)
    loaded = CheckpointReader().read(tmp_path)
    assert loaded is not None
    assert loaded.stage == "icps_done"
    assert loaded.problem_id == "P1"


def test_invalid_json_returns_none(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.json").write_text("not json {{{")
    assert CheckpointReader().read(tmp_path) is None


def test_checksum_mismatch_returns_none(tmp_path: Path) -> None:
    cp = RunCheckpoint(stage="started", checksum="A")
    CheckpointWriter().write(cp, tmp_path)
    assert CheckpointReader().read(tmp_path, expected_checksum="B") is None


def test_unknown_stage_returns_none(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.json").write_text(json.dumps({"stage": "bogus"}))
    assert CheckpointReader().read(tmp_path) is None
