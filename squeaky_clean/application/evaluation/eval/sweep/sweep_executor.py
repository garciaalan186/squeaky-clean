"""SweepExecutor: sweep orchestration POLICY, extracted from interface/cli (R6.7)."""

import time
from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.report.dashboard_generator import DashboardGenerator
from squeaky_clean.application.evaluation.eval.report.regression_gate import RegressionGate
from squeaky_clean.application.evaluation.eval.report.regression_writer import RegressionWriter
from squeaky_clean.application.evaluation.eval.resume.resume_helper import ResumeHelper
from squeaky_clean.application.evaluation.eval.run.meta_eval_paths import MetaEvalPaths
from squeaky_clean.application.evaluation.eval.sweep.sweep_dispatcher import SweepDispatcher
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.evaluation.eval.sweep.sweep_summary_writer import SweepSummaryWriter


class SweepExecutor:
    """Allocates one run dir, dispatches N problems, gates + summarizes."""

    def __init__(self, deps: SweepExecutorDeps) -> None:
        self._deps: SweepExecutorDeps = deps
        self._dispatcher: SweepDispatcher = SweepDispatcher(deps)
        self._summary: SweepSummaryWriter = SweepSummaryWriter()
        self._dashboard: DashboardGenerator = DashboardGenerator()
        self._resume: ResumeHelper = ResumeHelper()
        self._gate: RegressionGate = RegressionGate()
        self._regressions: RegressionWriter = RegressionWriter()

    def execute(self, request: SweepRequest) -> SweepResult:
        """Run every problem in ``request`` in parallel; return SweepResult."""
        run_dir = MetaEvalPaths(self._deps.run_root).allocate()
        self._deps.logger.event("sweep_started", run_dir=str(run_dir),
                                problems=[p.id for p in request.problems],
                                max_parallel=request.max_parallel)
        start = time.monotonic()
        bundles = self._dispatcher.dispatch(request, run_dir)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        result = SweepResult(
            run_dir=run_dir,
            bundles=bundles,
            total_cost_usd=sum(b.metrics.estimated_cost_usd for b in bundles),
            total_duration_ms=elapsed_ms,
        )
        result = self._assess_regressions(result)
        self._summary.write(result)
        self._write_dashboard(run_dir.parent)
        self._deps.logger.event("sweep_complete", run_dir=str(run_dir),
                                total_cost_usd=result.total_cost_usd,
                                total_duration_ms=elapsed_ms)
        return result

    def _assess_regressions(self, result: SweepResult) -> SweepResult:
        """R5.2: judge bundles against goldens; persist records; add verdicts."""
        assessment = self._gate.assess(result, self._deps.models())
        if assessment.records:
            self._regressions.write(
                assessment.records, result.run_dir / "regressions.json",
            )
        for verdict in assessment.verdicts:
            self._deps.logger.event("regression_gate", verdict=verdict)
        return replace(result, regression_verdicts=assessment.verdicts)

    def _write_dashboard(self, results_root: Path) -> None:
        target = results_root / "dashboard.html"
        try:
            self._dashboard.generate(results_root, target)
        except OSError as exc:
            self._deps.logger.event("dashboard_failed", error=str(exc))
