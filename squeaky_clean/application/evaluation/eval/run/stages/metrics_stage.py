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
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.emission.spec_conformance_checker import (
    SpecConformanceChecker,
)
from squeaky_clean.application.generation.testgen.check_test_obligations import CheckTestObligations
from squeaky_clean.application.generation.testgen.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.layer_type import LayerType


class MetricsStage:
    """Builds EvalMetrics from stage results; folds the stage counters in."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._assembler = MetricsInputsAssembler(
            deps.llm_usage_recorder, deps.model_router,
        )
        self._builder = RunEvalMetricsBuilder()

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
        c = ctx.counters
        metrics.infrastructure_choices_explicit = c.infra_explicit
        metrics.infrastructure_choices_derived = c.infra_derived
        metrics.mcda_runs = c.mcda_runs
        metrics.infrastructure_icp_count = sum(
            len(m.implemented_classes) for m in ctx.module_impls
            if m.module.layer is LayerType.INFRASTRUCTURE
        )
        metrics.dependency_install_failed = c.dep_install_failed
        metrics.http_convention_violations = c.http_violations
        metrics.architect_retries = c.architect_retries
        metrics.notation_novelty = c.notation_novelty
        metrics.test_criteria_filtered = c.test_criteria_filtered
        metrics.compile_errors = ctx.compile_errors
        metrics.spec_conformance_violations = len(
            SpecConformanceChecker().check(impl)
        )
        metrics.dependency_injection_violations = c.di_violations
        metrics.test_obligation_gaps = self._obligation_gaps(ctx)
        return metrics

    def _obligation_gaps(self, ctx: PipelineContext) -> int:
        """Deterministic count of spec obligations no generated test discharges."""
        if ctx.arch is None:
            return 0
        obligations = ProjectTestObligations().project(ctx.arch, ctx.problem)
        return len(CheckTestObligations().check(obligations, ctx.output_dir))
