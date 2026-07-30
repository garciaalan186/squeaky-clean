"""RunSweep: parallel multi-problem meta-evaluation orchestration."""

import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.report.dashboard_generator import DashboardGenerator
from squeaky_clean.application.evaluation.eval.report.regression_gate import RegressionGate
from squeaky_clean.application.evaluation.eval.report.regression_writer import RegressionWriter
from squeaky_clean.application.evaluation.eval.resume.resume_helper import ResumeHelper
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.meta_eval_paths import MetaEvalPaths
from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.sweep_failure_bundle import SweepFailureBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.evaluation.eval.sweep.sweep_summary_writer import SweepSummaryWriter
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.interface.cli.run_sweep_deps import RunSweepDeps

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_RUN_ROOT = _FRAMEWORK_ROOT.parent / "meta-evaluation-results"


class RunSweep:
    """Allocates one run dir, dispatches N problems via a thread pool."""

    def __init__(self, deps: RunSweepDeps, logger: RunLogger | None = None) -> None:
        self._deps: RunSweepDeps = deps
        self._summary: SweepSummaryWriter = SweepSummaryWriter()
        self._failure: SweepFailureBundle = SweepFailureBundle()
        self._logger: RunLogger = logger or NullRunLogger()
        self._dashboard: DashboardGenerator = DashboardGenerator()
        self._resume: ResumeHelper = ResumeHelper()
        self._gate: RegressionGate = RegressionGate()
        self._regressions: RegressionWriter = RegressionWriter()

    def execute(self, request: SweepRequest) -> SweepResult:
        """Run every problem in ``request`` in parallel; return SweepResult."""
        run_dir = MetaEvalPaths(
            self._deps.run_root or _DEFAULT_RUN_ROOT
        ).allocate()
        self._logger.event("sweep_started", run_dir=str(run_dir),
                           problems=[p.id for p in request.problems],
                           max_parallel=request.max_parallel)
        start = time.monotonic()
        bundles = self._dispatch(request, run_dir)
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
        self._logger.event("sweep_complete", run_dir=str(run_dir),
                           total_cost_usd=result.total_cost_usd,
                           total_duration_ms=elapsed_ms)
        return result

    def _assess_regressions(self, result: SweepResult) -> SweepResult:
        """R5.2: judge bundles against goldens; persist records; add verdicts."""
        models = {t.value: self._deps.router.route(t) for t in ModelTier}
        assessment = self._gate.assess(result, models)
        if assessment.records:
            self._regressions.write(
                assessment.records, result.run_dir / "regressions.json",
            )
        for verdict in assessment.verdicts:
            self._logger.event("regression_gate", verdict=verdict)
        return replace(result, regression_verdicts=assessment.verdicts)

    def _write_dashboard(self, results_root: Path) -> None:
        target = results_root / "dashboard.html"
        try:
            self._dashboard.generate(results_root, target)
        except OSError as exc:
            self._logger.event("dashboard_failed", error=str(exc))

    def _dispatch(
        self, request: SweepRequest, run_dir: Path,
    ) -> tuple[EvalReportBundle, ...]:
        results: dict[str, EvalReportBundle] = {}
        with ThreadPoolExecutor(max_workers=request.max_parallel) as pool:
            futures = {
                pool.submit(self._safe_one, problem, run_dir): problem
                for problem in request.problems
            }
            for fut in as_completed(futures):
                problem = futures[fut]
                results[problem.id] = fut.result()
        return tuple(results[p.id] for p in request.problems)

    def _safe_one(
        self, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        self._logger.event("problem_started", problem=problem.id,
                           target_language=problem.target_language.value)
        try:
            bundle = self._one(problem, run_dir)
            self._logger.event("problem_complete", problem=problem.id,
                               tests_pass=bundle.metrics.tests_pass,
                               cost_usd=bundle.metrics.estimated_cost_usd)
            return bundle
        except BudgetExceededError:
            # A budget breach is fatal to the whole sweep, not one problem:
            # the shared cap is spent, so remaining problems would only fail
            # or overspend. Log and propagate to abort the run loudly.
            self._logger.event("sweep_budget_exceeded", problem=problem.id,
                               error=traceback.format_exc().splitlines()[-1])
            raise
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            self._logger.event("problem_failed", problem=problem.id,
                               error=tb.splitlines()[-1] if tb else "")
            return self._failure.build(problem, tb)

    def _one(
        self, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        deps = self._deps.dependency_builder.build(self._deps.router, problem)
        return RunEval(deps, run_root=self._deps.run_root).execute_in(
            problem, run_dir,
        )
