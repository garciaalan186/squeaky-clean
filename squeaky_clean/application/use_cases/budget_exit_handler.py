"""BudgetExitHandler: builds a partial EvalReportBundle on budget breach."""

from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.budget_exit_writer import BudgetExitWriter
from squeaky_clean.application.use_cases.cost_gate import BudgetExceededError, CostGate


class BudgetExitHandler:
    """Produces a partial EvalReportBundle and BUDGET_EXIT.txt artifact."""

    def __init__(self, gate: CostGate | None) -> None:
        self._gate: CostGate | None = gate
        self._writer: BudgetExitWriter = BudgetExitWriter()

    def handle(
        self, problem: ProblemSpec, output_dir: Path,
        exc: BudgetExceededError,
    ) -> EvalReportBundle:
        """Persist BUDGET_EXIT.txt and return a partial EvalReportBundle."""
        spent = self._gate.spent_usd() if self._gate is not None else 0.0
        cap = (self._gate.budget().max_cost_usd
               if self._gate is not None else None)
        self._writer.write(output_dir, cap, spent, stage=str(exc))
        metrics = EvalMetrics.empty()
        metrics.budget_exceeded = True
        metrics.estimated_cost_usd = spent
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
