"""SweepDispatcher: thread-pool dispatch + per-problem error POLICY (R6.7)."""

import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.evaluation.eval.sweep.sweep_failure_bundle import SweepFailureBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec


class SweepDispatcher:
    """Runs every problem through the injected runner; owns the error policy."""

    def __init__(self, deps: SweepExecutorDeps) -> None:
        self._deps: SweepExecutorDeps = deps
        self._failure: SweepFailureBundle = SweepFailureBundle()

    def dispatch(
        self, request: SweepRequest, run_dir: Path,
    ) -> tuple[EvalReportBundle, ...]:
        """Run problems on a thread pool; return bundles in request order."""
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
        log = self._deps.logger
        log.event("problem_started", problem=problem.id,
                  target_language=problem.target_language.value)
        try:
            bundle = self._deps.runner(problem, run_dir)
            log.event("problem_complete", problem=problem.id,
                      tests_pass=bundle.metrics.tests_pass,
                      cost_usd=bundle.metrics.estimated_cost_usd)
            return bundle
        except (self._deps.replay_miss_error, BudgetExceededError) as exc:
            self._log_abort(problem, exc)
            raise
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            log.event("problem_failed", problem=problem.id,
                      error=tb.splitlines()[-1] if tb else "")
            return self._failure.build(problem, tb)

    def _log_abort(self, problem: ProblemSpec, exc: Exception) -> None:
        # A budget breach is fatal to the whole sweep, not one problem: the
        # shared cap is spent, so remaining problems would only fail or
        # overspend. R5.7: a replay-only cache miss is an infrastructure
        # signal (prompt drift / stale bundle), not a problem failure. Both
        # propagate so the run aborts loudly and the CI gate goes red
        # instead of reporting a green sweep.
        event = ("sweep_budget_exceeded" if isinstance(exc, BudgetExceededError)
                 else "replay_cache_miss")
        self._deps.logger.event(event, problem=problem.id,
                                error=traceback.format_exc().splitlines()[-1])
