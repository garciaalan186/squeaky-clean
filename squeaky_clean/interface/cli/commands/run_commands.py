"""RunCommands: single/replicated/sweep eval-run command flows."""

from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver
from squeaky_clean.interface.cli.replicates.replicate_runner import ReplicateRunner
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory
from squeaky_clean.interface.cli.run_sweep import RunSweep
from squeaky_clean.interface.cli.run_sweep_deps import RunSweepDeps


class RunCommands:
    """Executes the eval-run command family for one routed invocation."""

    def __init__(self, router: ModelRouter) -> None:
        self._router: ModelRouter = router

    def dispatch(self, problem: ProblemSpec, run: RunInvocation) -> int:
        """Run ``problem`` once or N times depending on ``run.replicates``."""
        if run.replicates > 1:
            return self._replicates(problem, run)
        return self._single_spec(problem, run)

    def single(self, problem_id: str, run: RunInvocation) -> int:
        """Resolve ``problem_id`` and dispatch it."""
        return self.dispatch(ProblemResolver().resolve(problem_id), run)

    def replicated(self, run: RunInvocation) -> int:
        """Run every requested problem through the N-replicate path."""
        codes = [
            self.dispatch(ProblemResolver().resolve(pid), run)
            for pid in run.problem_ids
        ]
        return max(codes)

    def sweep(self, run: RunInvocation) -> int:
        """Run the requested problems in parallel through RunSweep."""
        resolver = ProblemResolver()
        problems = tuple(resolver.resolve(pid) for pid in run.problem_ids)
        rc = RunConfigFactory().build(run.settings, replicate_id=0)
        deps = RunSweepDeps(
            dependency_builder=DependencyBuilder(self._router, rc),
            router=self._router,
        )
        result = RunSweep(deps, JSONLogger()).execute(SweepRequest(
            problems=problems, max_parallel=run.max_parallel,
        ))
        print(f"[squeaky] sweep complete: {result.run_dir}")
        print(f"[squeaky] {len(result.bundles)} problems, "
              f"${result.total_cost_usd:.4f}, {result.total_duration_ms}ms")
        return 0

    def _single_spec(self, problem: ProblemSpec, run: RunInvocation) -> int:
        rc = RunConfigFactory().build(run.settings, replicate_id=0)
        deps = DependencyBuilder(self._router, rc).build(problem)
        result = RunEval(deps).execute(problem)
        print(f"[squeaky] run complete: report at {result.report_path}")
        print(f"[squeaky] tests_pass={result.metrics.tests_pass:.2f} "
              f"cost=${result.metrics.estimated_cost_usd:.4f}")
        return 0

    def _replicates(self, problem: ProblemSpec, run: RunInvocation) -> int:
        runner = ReplicateRunner(self._router, run)
        summary = runner.run(problem)
        print(f"[squeaky] replicates complete: {summary.summary_path}")
        return 0
