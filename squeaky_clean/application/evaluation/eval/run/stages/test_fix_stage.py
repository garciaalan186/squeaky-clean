"""TestFixStage: test run, fixer loop, obligation + failing-test repair."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.fixer_loop import FixerLoop
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.repair.compile_gate import (
    CompileGate,
    CompileGateRequest,
)
from squeaky_clean.application.generation.repair.failing_tests_request import FailingTestsRequest
from squeaky_clean.application.generation.repair.fixer_stage import FixerStage
from squeaky_clean.application.generation.repair.repair_failing_tests import (
    RepairFailingTests,
)
from squeaky_clean.application.generation.repair.repair_obligation_gaps import (
    ObligationRepairRequest,
    RepairObligationGaps,
)
from squeaky_clean.application.generation.testgen.project_test_obligations import (
    ProjectTestObligations,
)


class TestFixStage:
    """Runs tests and the three repair feedback edges until green or spent."""

    def __init__(
        self, deps: RunEvalDependencies, fixer: FixerStage, gate: CompileGate,
    ) -> None:
        self._deps = deps
        self._loop = FixerLoop(deps, fixer)
        self._gate = gate

    def run(self, ctx: PipelineContext) -> PipelineContext:
        d = self._deps
        test_run = d.test_runner.run(ctx.output_dir)
        ctx.emitter.progress.tested()
        test_run, agg = self._loop.run(ctx, test_run)
        fix_stats = ctx.fix_stats
        arch = ctx.arch
        assert fix_stats is not None and arch is not None
        fix_stats = agg.merge(fix_stats)
        obligations = ProjectTestObligations().project(arch, ctx.problem)
        oblig = RepairObligationGaps(d.test_repairer).run(
            ObligationRepairRequest(
                obligations, ctx.output_dir, d.toolkit, self._max_passes()))
        if oblig.usage.classes_fixed > 0:
            impl = ctx.impl
            assert impl is not None
            self._gate.run(CompileGateRequest(
                implementation=impl, output_dir=ctx.output_dir,
                max_passes=self._max_passes(), architecture=ctx.arch,
                toolkit=d.toolkit))
            test_run = d.test_runner.run(ctx.output_dir)
            fix_stats = fix_stats.merge(oblig.usage)
        if test_run.failed > 0:
            crash = RepairFailingTests(d.test_repairer).run(
                FailingTestsRequest(
                    test_run.raw_output, ctx.output_dir, d.toolkit))
            if crash.classes_fixed > 0:
                test_run = d.test_runner.run(ctx.output_dir)
                fix_stats = fix_stats.merge(crash)
        ctx.emitter.progress.fixed(fix_stats.passes)
        ctx.lifecycle.record_fields("tests_complete", {
            "all_passed": test_run.failed == 0 and test_run.errors == 0,
            "passed": test_run.passed,
            "failed": test_run.failed,
            "errors": test_run.errors,
        })
        func_run = (d.functional_test_runner.run(ctx.output_dir)
                    if d.functional_test_runner else None)
        return replace(
            ctx, test_run=test_run, func_run=func_run, fix_stats=fix_stats)

    def _max_passes(self) -> int:
        return int(self._deps.run_config.retry_policy.max_fixer_passes)
