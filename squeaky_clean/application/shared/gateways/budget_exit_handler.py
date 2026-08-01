"""BudgetExitHandler: builds a partial EvalReportBundle on budget breach."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.gateways.budget_exit_writer import BudgetExitWriter
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError, CostGate
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class BudgetExitHandler:
    """Produces a partial EvalReportBundle and BUDGET_EXIT.txt artifact.

    Constructed per aborted run: ``problem`` is the run being abandoned.
    """

    def __init__(self, gate: CostGate | None, problem: ProblemSpec) -> None:
        self._gate: CostGate | None = gate
        self._problem: ProblemSpec = problem

    def handle(
        self, output_dir: Path, exc: BudgetExceededError,
    ) -> EvalReportBundle:
        """Persist BUDGET_EXIT.txt and return a partial EvalReportBundle."""
        problem = self._problem
        spent = self._gate.spent_usd() if self._gate is not None else 0.0
        cap = (self._gate.budget.max_cost_usd
               if self._gate is not None else None)
        BudgetExitWriter(cap, spent).write(output_dir, stage=str(exc))
        metrics = EvalMetrics(
            budget_exceeded=True,
            cost=CostBreakdown(estimated_cost_usd=spent),
        )
        empty_run = TestRunResult(
            passed=0, failed=0, errors=0, duration_ms=0,
            raw_output="aborted: budget exceeded",
        )
        return EvalReportBundle(
            problem=problem, metrics=metrics,
            test_run_result=empty_run,
            validation=ValidationReport(violations=(), files_scanned=0),
            error=f"budget exceeded: {exc}",
        )
