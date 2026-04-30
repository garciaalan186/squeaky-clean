"""Integration tests for the resume pipeline (G3)."""

import json
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.use_cases.checkpoint_checksum import CheckpointChecksum
from squeaky_clean.application.use_cases.checkpoint_writer import CheckpointWriter
from squeaky_clean.application.use_cases.resume_run import ResumeRun
from squeaky_clean.application.use_cases.run_eval import RunEval
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _allocate(tmp_path: Path) -> Path:
    deps = build_stub_deps()
    RunEval(deps, run_root=tmp_path).execute(P0)
    return next(iter(tmp_path.iterdir()))


def test_full_pipeline_emits_complete_checkpoint(tmp_path: Path) -> None:
    run_dir = _allocate(tmp_path)
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    cp_path = ps_dir / "CHECKPOINT.json"
    assert cp_path.exists()
    data = json.loads(cp_path.read_text())
    assert data["stage"] == "complete"
    assert data["problem_id"] == "P0"


def test_resume_complete_short_circuits(tmp_path: Path) -> None:
    run_dir = _allocate(tmp_path)
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    deps = build_stub_deps()
    bundle = ResumeRun().resume(ps_dir, P0, deps)
    assert "resumed" in bundle.test_run_result.raw_output
    assert deps.design_architecture.execute.call_count == 0  # type: ignore[attr-defined]


def test_resume_checksum_mismatch_falls_back(tmp_path: Path) -> None:
    ps_dir = tmp_path / "ps"
    ps_dir.mkdir()
    cp = RunCheckpoint(stage="icps_done", problem_id="P0", checksum="WRONG")
    CheckpointWriter().write(cp, ps_dir)
    deps = build_stub_deps()
    bundle = ResumeRun().resume(ps_dir, P0, deps)
    # Fallback runs full pipeline → architect IS called
    assert deps.design_architecture.execute.call_count == 1  # type: ignore[attr-defined]
    assert bundle.metrics.estimated_cost_usd > 0


def test_resume_from_icps_done_skips_architect(tmp_path: Path) -> None:
    """Pre-populate a checkpoint at icps_done; resume must skip architect+ICPs."""
    run_dir = _allocate(tmp_path)
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    data = json.loads((ps_dir / "CHECKPOINT.json").read_text())
    # Rewrite stage to icps_done so resume must use cached impls
    data["stage"] = "icps_done"
    (ps_dir / "CHECKPOINT.json").write_text(json.dumps(data))
    deps = build_stub_deps()
    ResumeRun().resume(ps_dir, P0, deps)
    assert deps.design_architecture.execute.call_count == 0  # type: ignore[attr-defined]
    assert deps.orchestrate_module.execute.call_count == 0  # type: ignore[attr-defined]


def test_checksum_helper_is_stable() -> None:
    a = CheckpointChecksum().compute("P0")
    b = CheckpointChecksum().compute("P0")
    assert a == b
    assert a != CheckpointChecksum().compute("P1")


def test_resume_missing_checkpoint_runs_full(tmp_path: Path) -> None:
    """No CHECKPOINT.json → fall back to a full pipeline run."""
    deps = build_stub_deps()
    target = tmp_path / "missing"
    target.mkdir()
    bundle = ResumeRun().resume(target, P0, deps)
    # Full run: architect IS called
    assert deps.design_architecture.execute.call_count == 1  # type: ignore[attr-defined]
    assert bundle is not None
