"""Test that RunEvalPipeline gracefully aborts and writes partial results."""

import json
from dataclasses import replace
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.cost_gate import BudgetExceededError, CostGate
from squeaky_clean.application.use_cases.run_eval import RunEval
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _exhausted_gate() -> CostGate:
    gate = CostGate(CostBudget(max_cost_usd=0.01))
    gate.record(0.005)
    return gate


def test_pipeline_exits_gracefully_on_budget_breach(tmp_path: Path) -> None:
    base = build_stub_deps()
    gate = _exhausted_gate()

    def boom(_p: ProblemSpec) -> ArchitectureSpec:
        raise BudgetExceededError("spend exceeded")

    base.design_architecture.execute = boom  # type: ignore[assignment,method-assign]
    deps = replace(base, cost_gate=gate)
    result = RunEval(deps, run_root=tmp_path).execute(P0)
    run_dir = next(iter(tmp_path.iterdir()))
    ps_dir = run_dir / "problem-set-0-calculator_python-code"
    assert (ps_dir / "BUDGET_EXIT.txt").exists()
    body = (ps_dir / "BUDGET_EXIT.txt").read_text()
    assert "cap:" in body and "spent:" in body
    report = json.loads((ps_dir / "eval_report.json").read_text())
    assert report["metrics"]["budget_exceeded"] is True
    assert report["metrics"]["estimated_cost_usd"] == 0.005
    assert result.metrics.budget_exceeded is True
