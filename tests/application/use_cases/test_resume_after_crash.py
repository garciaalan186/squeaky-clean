"""Test: pipeline crashes after icps_done, resume picks up cached impls (G3)."""

import json
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.use_cases.resume_run import ResumeRun
from squeaky_clean.application.use_cases.run_eval import RunEval
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def test_crash_after_icps_then_resume(tmp_path: Path) -> None:
    """Force the pipeline to crash post-icps; resume reuses cached state."""
    deps = build_stub_deps()

    def boom(*a: object, **kw: object) -> object:
        raise RuntimeError("simulated mid-pipeline crash")

    deps.integrate_module.execute.side_effect = boom  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError, match="simulated"):
        RunEval(deps, run_root=tmp_path).execute(P0)
    run_dir = next(iter(tmp_path.iterdir()))
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    cp_data = json.loads((ps_dir / "CHECKPOINT.json").read_text())
    assert cp_data["stage"] == "icps_done"
    assert (ps_dir / "_resume_module_impls.json").exists()
    fresh = build_stub_deps()
    ResumeRun().resume(ps_dir, P0, fresh)
    assert fresh.design_architecture.execute.call_count == 0  # type: ignore[attr-defined]
    assert fresh.orchestrate_module.execute.call_count == 0  # type: ignore[attr-defined]
    assert fresh.integrate_module.execute.call_count == 1  # type: ignore[attr-defined]
