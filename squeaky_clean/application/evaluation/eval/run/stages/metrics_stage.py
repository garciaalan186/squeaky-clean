"""MetricsStage: assemble PipelineOutputs into EvalMetrics + fold counters."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs_assembler import (
    MetricsInputsAssembler,
)
from squeaky_clean.application.evaluation.eval.run.pipeline_outputs import PipelineOutputs
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.run_eval_metrics_builder import (
    RunEvalMetricsBuilder,
)
from squeaky_clean.application.evaluation.eval.run.stages.counter_fold import CounterFold
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics


class MetricsStage:
    """Builds EvalMetrics from stage results; folds the stage counters in."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._assembler = MetricsInputsAssembler(
            deps.llm_usage_recorder, deps.model_router,
        )
        self._builder = RunEvalMetricsBuilder()
        self._fold = CounterFold()

    def build(self, ctx: PipelineContext) -> EvalMetrics:
        impl, test_run, validation, fix_stats = (
            ctx.impl, ctx.test_run, ctx.validation, ctx.fix_stats)
        assert impl is not None and test_run is not None
        assert validation is not None and fix_stats is not None
        assert ctx.sec_arch is not None
        outputs = PipelineOutputs(
            implementation=impl, test_run=test_run, validation=validation,
            func_run=ctx.func_run, security_architecture=ctx.sec_arch,
            fix_stats=fix_stats,
            wall_clock_ms=ctx.lifecycle.elapsed_ms(
                "squib_parse_start", "tests_complete") or 0,
        )
        inputs = self._assembler.assemble(outputs, ctx.output_dir)
        metrics = self._builder.build(inputs)
        return self._fold.apply(ctx, metrics)
