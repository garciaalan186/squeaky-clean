"""ReplicateRunner: run one problem N times and aggregate metrics."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.eval_result_dto import EvalResult
from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.replicate_aggregator import ReplicateAggregator
from squeaky_clean.application.evaluation.eval.sweep.replicate_report import ReplicateReport
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary_writer import (
    ReplicateSummaryWriter,
)
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.llm.replay_cache_miss_error import ReplayCacheMissError
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.invocations.run_settings import RunSettings
from squeaky_clean.interface.cli.replicates.replicate_calibration_error import (
    ReplicateCalibrationError,
)
from squeaky_clean.interface.cli.replicates.replicate_run_outcome import ReplicateRunOutcome
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


class ReplicateRunner:
    """Run a problem with seeds 0..N-1; aggregate metrics into mean ± stddev."""

    def __init__(self, router: ModelRouter, invocation: RunInvocation) -> None:
        self._router: ModelRouter = router
        self._invocation: RunInvocation = invocation
        self._rc_factory: RunConfigFactory = RunConfigFactory()
        self._aggregator: ReplicateAggregator = ReplicateAggregator()
        self._writer: ReplicateSummaryWriter = ReplicateSummaryWriter()

    def run(self, problem: ProblemSpec) -> ReplicateRunOutcome:
        """Run the invocation's replicates; write replicate_summary.{json,md}."""
        results: list[EvalResult] = []
        failures: list[str] = []
        for r in range(self._invocation.replicates):
            rc = self._rc_factory.build(
                self._with_seed(self._invocation.settings, r), replicate_id=r,
            )
            deps = DependencyBuilder(self._router, rc).build(problem)
            try:
                results.append(RunEval(deps).execute(problem))
            except (BudgetExceededError, ReplayCacheMissError):
                raise  # infrastructure signals abort the whole calibration
            except Exception as exc:  # noqa: BLE001 — replicate isolation
                failures.append(f"replicate {r}: {type(exc).__name__}: {exc}")
        if not results:
            raise ReplicateCalibrationError(
                f"{problem.id}: all {self._invocation.replicates} replicates "
                "failed — " + "; ".join(failures)
            )
        return self._write_summary(problem, results, tuple(failures))

    @staticmethod
    def _with_seed(settings: RunSettings, replicate: int) -> RunSettings:
        # replace() preserves every flag (rebuilding field-by-field dropped them).
        return replace(settings, seed=replicate)

    def _write_summary(
        self, problem: ProblemSpec, results: list[EvalResult],
        failures: tuple[str, ...] = (),
    ) -> ReplicateRunOutcome:
        summary = self._aggregator.aggregate(
            problem.id, [r.metrics for r in results],
        )
        # <run_dir>/problem-set-*-code/eval_report.json -> first run dir.
        first_dir = results[0].report_path.parent.parent
        json_path = self._writer.write(first_dir, ReplicateReport(
            summary=summary,
            report_paths=tuple(str(r.report_path) for r in results),
            failures=failures,
        ))
        return ReplicateRunOutcome(summary_path=json_path, runs=len(results))
