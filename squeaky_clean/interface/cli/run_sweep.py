"""RunSweep: humble CLI wiring — sweep POLICY lives in SweepExecutor (R6.7)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor import SweepExecutor
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.replay_cache_miss_error import (
    ReplayCacheMissError,
)
from squeaky_clean.interface.cli.run_sweep_deps import RunSweepDeps

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_RUN_ROOT = _FRAMEWORK_ROOT.parent / "meta-evaluation-results"


class RunSweep:
    """Builds the boundary callables and delegates the sweep to SweepExecutor."""

    def __init__(self, deps: RunSweepDeps, logger: RunLogger | None = None) -> None:
        self._deps: RunSweepDeps = deps
        self._logger: RunLogger = logger or NullRunLogger()

    def execute(self, request: SweepRequest) -> SweepResult:
        """Run every problem in ``request`` in parallel; return SweepResult."""
        return SweepExecutor(SweepExecutorDeps(
            run_root=self._deps.run_root or _DEFAULT_RUN_ROOT,
            runner=self._run_one,
            models=self._models,
            logger=self._logger,
            replay_miss_error=ReplayCacheMissError,
        )).execute(request)

    def _models(self) -> dict[str, str]:
        return {t.value: self._deps.router.route(t) for t in ModelTier}

    def _run_one(self, problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        deps = self._deps.dependency_builder.build(problem)
        return RunEval(deps, run_root=self._deps.run_root).execute_in(
            problem, run_dir,
        )
