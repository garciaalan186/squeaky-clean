"""CounterFold: fold PipelineContext counters into a frozen EvalMetrics."""

from __future__ import annotations

from dataclasses import replace

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


class CounterFold:
    """Returns a new EvalMetrics with the stage counters folded in."""

    def apply(self, ctx: PipelineContext, metrics: EvalMetrics) -> EvalMetrics:
        """Fold ``ctx.counters`` + conformance checks into ``metrics``."""
        impl = ctx.impl
        assert impl is not None
        c = ctx.counters
        notation = replace(
            metrics.notation,
            infrastructure_choices_explicit=c.infra_explicit,
            infrastructure_choices_derived=c.infra_derived,
            mcda_runs=c.mcda_runs,
            infrastructure_icp_count=sum(
                len(m.implemented_classes) for m in ctx.module_impls
                if m.module.layer is LayerType.INFRASTRUCTURE
            ),
            dependency_install_failed=c.dep_install_failed,
            http_convention_violations=c.http_violations,
            notation_novelty=c.notation_novelty,
            test_criteria_filtered=c.test_criteria_filtered,
            spec_conformance_violations=len(
                SpecConformanceChecker().check(impl)
            ),
            dependency_injection_violations=c.di_violations,
            test_obligation_gaps=self._obligation_gaps(ctx),
        )
        reliability = replace(
            metrics.reliability,
            architect_retries=c.architect_retries,
            compile_errors=ctx.compile_errors,
        )
        return replace(metrics, notation=notation, reliability=reliability)

    def _obligation_gaps(self, ctx: PipelineContext) -> int:
        """Deterministic count of spec obligations no generated test discharges."""
        if ctx.arch is None:
            return 0
        obligations = ProjectTestObligations().project(ctx.arch, ctx.problem)
        return len(CheckTestObligations().check(obligations, ctx.output_dir))
