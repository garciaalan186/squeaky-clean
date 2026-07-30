"""ReplicateRunner: run one problem N times and aggregate metrics."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_result_dto import EvalResult
from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.replicate_aggregator import (
    ReplicateAggregator,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_report import (
    ReplicateReport,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary_writer import (
    ReplicateSummaryWriter,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


@dataclass(frozen=True)
class ReplicateRunOutcome:
    """Aggregated multi-replicate result with summary file path."""

    summary_path: Path
    runs: int


class ReplicateRunner:
    """Run a problem with seeds 0..N-1; aggregate metrics into mean ± stddev."""

    def __init__(
        self, builder: DependencyBuilder, rc_factory: RunConfigFactory,
    ) -> None:
        self._builder: DependencyBuilder = builder
        self._rc_factory: RunConfigFactory = rc_factory
        self._aggregator: ReplicateAggregator = ReplicateAggregator()
        self._writer: ReplicateSummaryWriter = ReplicateSummaryWriter()

    def run(
        self, router: ModelRouter, problem: ProblemSpec, args: CLIArgs,
    ) -> ReplicateRunOutcome:
        """Run ``args.replicates`` replicates; write replicate_summary.{json,md}."""
        results: list[EvalResult] = []
        for r in range(args.replicates):
            seed_args = self._with_seed(args, r)
            rc = self._rc_factory.build(seed_args, replicate_id=r)
            deps = self._builder.build(router, problem, rc)
            results.append(RunEval(deps).execute(problem))
        return self._write_summary(problem, results)

    @staticmethod
    def _with_seed(args: CLIArgs, replicate: int) -> CLIArgs:
        # dataclasses.replace preserves every flag (cost cap, security tests,
        # cache config, ...) — rebuilding field-by-field silently dropped them.
        return replace(args, seed=replicate)

    def _write_summary(
        self, problem: ProblemSpec, results: list[EvalResult],
    ) -> ReplicateRunOutcome:
        summary = self._aggregator.aggregate(
            problem.id, [r.metrics for r in results],
        )
        # report_path = <run_dir>/problem-set-*-code/eval_report.json; the
        # summary belongs in the FIRST replicate's run dir (two levels up —
        # three landed it in the shared results root, orphaned from its run).
        first_dir = results[0].report_path.parent.parent
        json_path = self._writer.write(first_dir, ReplicateReport(
            summary=summary,
            report_paths=tuple(str(r.report_path) for r in results),
        ))
        return ReplicateRunOutcome(summary_path=json_path, runs=len(results))
