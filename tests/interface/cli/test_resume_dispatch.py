"""Tests for ResumeDispatch problem resolution (no pipeline is run)."""

import json
from pathlib import Path

import pytest

from squeaky_clean.interface.cli.invocations.maintenance_invocation import (
    MaintenanceInvocation,
)
from squeaky_clean.interface.cli.resume_dispatch import ResumeDispatch


def test_explicit_problem_id_wins_over_checkpoint(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.json").write_text(json.dumps({"problem_id": "P1"}))
    inv = MaintenanceInvocation(resume_run_dir=str(tmp_path), problem_ids=("P0",))
    assert ResumeDispatch()._resolve_problem(tmp_path, inv).id == "P0"


def test_checkpoint_problem_id_used_when_no_flag_given(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.json").write_text(json.dumps({"problem_id": "P1"}))
    inv = MaintenanceInvocation(resume_run_dir=str(tmp_path))
    assert ResumeDispatch()._resolve_problem(tmp_path, inv).id == "P1"


def test_missing_checkpoint_raises_value_error(tmp_path: Path) -> None:
    inv = MaintenanceInvocation(resume_run_dir=str(tmp_path))
    with pytest.raises(ValueError, match="cannot resume"):
        ResumeDispatch()._resolve_problem(tmp_path, inv)


def test_checkpoint_with_empty_problem_id_raises(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.json").write_text(json.dumps({"problem_id": ""}))
    inv = MaintenanceInvocation(resume_run_dir=str(tmp_path))
    with pytest.raises(ValueError, match="cannot resume"):
        ResumeDispatch()._resolve_problem(tmp_path, inv)
