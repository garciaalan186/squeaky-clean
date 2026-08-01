"""FinalizeStage: security scan, ACS, percentiles, contract registration."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.metrics.architectural_complexity_scorer import (  # noqa: E501
    ArchitecturalComplexityScorer,
)
from squeaky_clean.application.evaluation.eval.report.percentile_summary_renderer import (
    PercentileSummaryRenderer,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.security.security_scan_stage import SecurityScanStage
from squeaky_clean.application.generation.validation.contract_registry import ContractRegistry
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics


class FinalizeStage:
    """Post-metrics enrichment and run-closing artifacts."""

    def __init__(
        self, deps: RunEvalDependencies, contracts: ContractRegistry,
    ) -> None:
        self._deps = deps
        self._logger = deps.run_logger
        self._contracts = contracts
        self._security = SecurityScanStage(
            deps.secret_path_scanner, deps.sast_runner,
        )

    def finalize(self, ctx: PipelineContext, metrics: EvalMetrics) -> None:
        self._security.apply(
            ctx.output_dir, metrics, self._deps.run_config.enable_sast,
        )
        self._populate_acs(ctx, metrics)
        section = PercentileSummaryRenderer().render(
            self._deps.llm_usage_recorder)
        if section:
            try:
                (ctx.output_dir / "LATENCY_PERCENTILES.md").write_text(section)
            except OSError as exc:
                self._logger.event("percentiles_write_failed", error=str(exc))
        self._register_produced(ctx)
        ctx.emitter.complete(metrics.estimated_cost_usd)

    def _populate_acs(self, ctx: PipelineContext, metrics: EvalMetrics) -> None:
        """Compute Architectural Complexity Score + normalized derivatives."""
        arch = ctx.arch
        assert arch is not None
        score = ArchitecturalComplexityScorer().score(
            ctx.problem, arch, ctx.output_dir / "src",
        )
        metrics.acs_structural = score.structural
        metrics.acs_codegen = score.codegen
        metrics.acs_constraint = score.constraint
        metrics.acs_composite = score.composite
        metrics.acs_normalized = score.normalized
        if score.composite > 0:
            metrics.acs_cost_per_unit = round(
                metrics.estimated_cost_usd / score.composite, 4,
            )
            # Only a real, measured wall-clock yields a meaningful velocity
            # (a floor once turned cache-served runs into composite*1000/s).
            if metrics.total_wall_clock_ms > 0:
                wall_s = metrics.total_wall_clock_ms / 1000.0
                metrics.acs_velocity = round(score.composite / wall_s, 3)

    def _register_produced(self, ctx: PipelineContext) -> None:
        for c in ctx.problem.produces_contracts:
            stamped = c if c.producer_problem_id else type(c)(
                name=c.name, transport=c.transport, fields=c.fields,
                producer_problem_id=ctx.problem.id)
            try:
                self._contracts.register(stamped)
            except OSError as exc:
                self._logger.event(
                    "contract_register_failed",
                    contract=c.name, error=str(exc))
