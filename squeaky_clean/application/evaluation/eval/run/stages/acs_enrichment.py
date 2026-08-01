"""AcsEnrichment: fold Architectural Complexity Score into EvalMetrics."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.metrics.architectural_complexity_scorer import (  # noqa: E501
    ArchitecturalComplexityScorer,
)
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext


class AcsEnrichment:
    """Computes ACS + normalized derivatives; returns a new EvalMetrics."""

    def enrich(
        self, ctx: PipelineContext, metrics: EvalMetrics,
    ) -> EvalMetrics:
        """Return ``metrics`` with StructureStats ACS fields populated."""
        arch = ctx.arch
        assert arch is not None
        score = ArchitecturalComplexityScorer(ctx.output_dir / "src").score(
            ctx.problem, arch,
        )
        cost_per_unit, velocity = 0.0, 0.0
        if score.composite > 0:
            cost_per_unit = round(
                metrics.estimated_cost_usd / score.composite, 4,
            )
            # Only a real, measured wall-clock yields a meaningful velocity
            # (a floor once turned cache-served runs into composite*1000/s).
            if metrics.total_wall_clock_ms > 0:
                wall_s = metrics.total_wall_clock_ms / 1000.0
                velocity = round(score.composite / wall_s, 3)
        structure = replace(
            metrics.structure,
            acs_structural=score.structural,
            acs_codegen=score.codegen,
            acs_constraint=score.constraint,
            acs_composite=score.composite,
            acs_normalized=score.normalized,
            acs_cost_per_unit=cost_per_unit,
            acs_velocity=velocity,
        )
        return replace(metrics, structure=structure)
