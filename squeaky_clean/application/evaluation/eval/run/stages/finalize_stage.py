"""FinalizeStage: security scan, ACS, percentiles, contract registration."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.report.percentile_summary_renderer import (
    PercentileSummaryRenderer,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.acs_enrichment import AcsEnrichment
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.security.security_scan_stage import SecurityScanStage
from squeaky_clean.application.generation.validation.contract_registry import ContractRegistry
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text


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
            logger=deps.run_logger,
        )

    def finalize(
        self, ctx: PipelineContext, metrics: EvalMetrics,
    ) -> EvalMetrics:
        """Return ``metrics`` enriched with scan + ACS results (frozen)."""
        metrics = replace(metrics, security_scan=self._security.apply(
            ctx.output_dir, self._deps.run_config.enable_sast))
        metrics = AcsEnrichment().enrich(ctx, metrics)
        section = PercentileSummaryRenderer().render(
            self._deps.llm_usage_recorder)
        if section:
            try:
                atomic_write_text(
                    ctx.output_dir / "LATENCY_PERCENTILES.md", section)
            except OSError as exc:
                self._logger.event("percentiles_write_failed", error=str(exc))
        self._register_produced(ctx)
        ctx.emitter.progress.complete(metrics.estimated_cost_usd)
        return metrics

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
