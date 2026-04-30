"""Tests for the RunEval use case with stubbed pipeline collaborators."""

import json
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.use_cases.run_eval import RunEval
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def test_run_eval_writes_all_artifacts(tmp_path: Path) -> None:
    result = RunEval(build_stub_deps(), run_root=tmp_path).execute(P0)
    run_dir = next(iter(tmp_path.iterdir()))
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "SUMMARY.md").exists()
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    assert (ps_dir / "eval_report.json").exists()
    metrics = json.loads((run_dir / "metrics.json").read_text())
    assert metrics["estimated_cost_usd"] == 0.12
    assert metrics["total_wall_clock_ms"] == 3400
    assert abs(metrics["tests_pass"] - (2 / 3)) < 1e-9
    assert metrics["total_tokens_input"] == 111
    assert metrics["total_tokens_output"] == 222
    assert metrics["parallelism_limit"] == 4
    assert metrics["peak_parallelism"] == 1
    assert metrics["classes_per_module"] == [1]
    assert result.problem_id == "P0"
