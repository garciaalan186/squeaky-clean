"""ReplicateRunner: run one problem N times and aggregate metrics."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.eval_result_dto import EvalResult
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.run_eval import RunEval
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


@dataclass(frozen=True)
class ReplicateSummary:
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

    def run(
        self, router: ModelRouter, problem: ProblemSpec, args: CLIArgs,
    ) -> ReplicateSummary:
        """Run ``args.replicates`` replicates; write replicate_summary.json."""
        results: list[EvalResult] = []
        for r in range(args.replicates):
            seed_args = self._with_seed(args, r)
            rc = self._rc_factory.build(seed_args, replicate_id=r)
            deps = self._builder.build(router, problem, rc)
            results.append(RunEval(deps).execute(problem))
        return self._write_summary(results)

    @staticmethod
    def _with_seed(args: CLIArgs, replicate: int) -> CLIArgs:
        return CLIArgs(
            problem_ids=args.problem_ids,
            model_override=args.model_override,
            max_parallel=args.max_parallel,
            replicates=args.replicates,
            problem_file=args.problem_file,
            seed=replicate,
            temperature_architect=args.temperature_architect,
            temperature_icp=args.temperature_icp,
            deterministic=args.deterministic,
        )

    def _write_summary(self, results: list[EvalResult]) -> ReplicateSummary:
        first_dir = results[0].report_path.parent.parent.parent
        summary_path = first_dir / "replicate_summary.json"
        passes = [r.metrics.tests_pass for r in results]
        costs = [r.metrics.estimated_cost_usd for r in results]
        payload = {
            "runs": len(results),
            "tests_pass_mean": statistics.fmean(passes) if passes else 0.0,
            "tests_pass_stdev": statistics.stdev(passes) if len(passes) > 1 else 0.0,
            "cost_mean": statistics.fmean(costs) if costs else 0.0,
            "cost_stdev": statistics.stdev(costs) if len(costs) > 1 else 0.0,
            "reports": [str(r.report_path) for r in results],
        }
        summary_path.write_text(json.dumps(payload, indent=2))
        return ReplicateSummary(summary_path=summary_path, runs=len(results))
