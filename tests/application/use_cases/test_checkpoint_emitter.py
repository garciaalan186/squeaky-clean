"""Tests for CheckpointEmitter staged writes (G3)."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.use_cases.checkpoint_emitter import CheckpointEmitter
from tests.application.use_cases.run_eval_stub_deps import _impl


def _read(run_dir: Path) -> dict[str, object]:
    data: dict[str, object] = json.loads((run_dir / "CHECKPOINT.json").read_text())
    return data


def test_initial_state_is_started(tmp_path: Path) -> None:
    CheckpointEmitter("P0", tmp_path)
    data = _read(tmp_path)
    assert data["stage"] == "started"
    assert data["problem_id"] == "P0"
    assert data["checksum"]


def test_each_stage_advances(tmp_path: Path) -> None:
    e = CheckpointEmitter("P0", tmp_path)
    e.architect_done("MODULE X\n")
    assert _read(tmp_path)["stage"] == "architect_done"
    empty = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    e.test_arch_done(empty, empty)
    assert _read(tmp_path)["stage"] == "test_arch_done"
    impls: tuple[ModuleImplementation, ...] = (_impl(),)
    e.icps_done(impls)
    assert _read(tmp_path)["stage"] == "icps_done"
    assert (tmp_path / "_resume_module_impls.json").exists()
    e.integrated()
    assert _read(tmp_path)["stage"] == "integrated"
    e.tested()
    assert _read(tmp_path)["stage"] == "tested"
    e.fixed(2)
    after_fixed = _read(tmp_path)
    assert after_fixed["stage"] == "fixed"
    assert after_fixed["fixer_passes_completed"] == 2
    e.complete(0.42)
    final = _read(tmp_path)
    assert final["stage"] == "complete"
    assert final["cost_spent_usd"] == 0.42
