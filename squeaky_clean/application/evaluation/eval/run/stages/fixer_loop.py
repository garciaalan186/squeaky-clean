"""FixerLoop: bounded fix-and-retest loop until tests pass or fixes dry up."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.repair.fix_request import FixRequest
from squeaky_clean.application.generation.repair.fixer_stage import FixerStage, FixerStageResult
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class FixerLoop:
    """Runs FixerStage up to ``max_fixer_passes`` times until tests pass."""

    def __init__(self, deps: RunEvalDependencies, fixer: FixerStage) -> None:
        self._deps = deps
        self._fixer = fixer

    def run(
        self, ctx: PipelineContext, test_run: TestRunResult,
    ) -> tuple[TestRunResult, FixerStageResult]:
        agg = FixerStageResult(0, 0, 0, 0.0, 0, 0)
        cur_run = test_run
        max_passes = int(self._deps.run_config.retry_policy.max_fixer_passes)
        for _ in range(max_passes):
            if cur_run.failed == 0 and cur_run.errors == 0:
                break
            impl = ctx.impl
            assert impl is not None
            stats = self._fixer.apply(
                FixRequest(implementation=impl, test_run_result=cur_run,
                           architecture=ctx.arch),
                ctx.output_dir,
            )
            agg = agg.merge(stats)
            if stats.classes_fixed == 0:
                break
            cur_run = self._deps.test_runner.run(ctx.output_dir)
        return cur_run, agg
