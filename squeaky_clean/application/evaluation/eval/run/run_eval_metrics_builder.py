"""RunEvalMetricsBuilder: build one frozen EvalMetrics from pipeline outputs."""

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.metrics.cache_savings_calculator import (
    CacheSavingsCalculator,
)
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.notation_stats import NotationStats
from squeaky_clean.application.evaluation.eval.metrics.model.reliability_stats import (
    ReliabilityStats,
)
from squeaky_clean.application.evaluation.eval.metrics.model.structure_stats import StructureStats
from squeaky_clean.application.evaluation.eval.metrics.model.tier_cache_stats import TierCacheStats
from squeaky_clean.application.evaluation.eval.metrics.model.velocity_stats import VelocityStats
from squeaky_clean.application.evaluation.eval.run.run_eval_test_outcome import (
    RunEvalTestOutcome,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_token_mapper import RunEvalTokenMapper
from squeaky_clean.application.evaluation.eval.run.run_eval_velocity import RunEvalVelocity

_PARALLELISM_LIMIT: int = 4


class RunEvalMetricsBuilder:
    """Derive a frozen EvalMetrics from the outputs of one pipeline run."""

    def build(self, inputs: MetricsInputs) -> EvalMetrics:
        """Return the EvalMetrics computed from ``inputs`` in one shot."""
        impl = inputs.implementation
        cache_by_tier, cache_savings = self._cache_breakdown(inputs)
        m = EvalMetrics(
            test_outcome=RunEvalTestOutcome().build(inputs),
            cost=RunEvalTokenMapper().map(inputs),
            velocity=VelocityStats(
                artifact_token_estimate=inputs.file_stats.artifact_char_count // 4,
            ),
            structure=self._structure(inputs),
            reliability=self._reliability(inputs),
            notation=NotationStats(
                spec_conformance_violations=inputs.spec_conformance_violations,
                composer_validation_failures=inputs.composer_validation_failures,
                composer_manager_fallback_calls=(
                    inputs.composer_manager_fallback_calls
                ),
            ),
            architecture_violations=len(inputs.validation.violations),
            total_wall_clock_ms=inputs.wall_clock_ms or impl.total_duration_ms,
            parallelism_limit=_PARALLELISM_LIMIT,
            peak_parallelism=min(
                len(impl.implemented_classes), _PARALLELISM_LIMIT,
            ),
            cache_by_tier=cache_by_tier,
            cache_creation_input_tokens=inputs.cache_creation_input_tokens,
            cache_read_input_tokens=inputs.cache_read_input_tokens,
            cache_hit_count=inputs.cache_hit_count,
            cache_miss_count=inputs.cache_miss_count,
            cache_savings_usd=cache_savings,
            replicate_id=inputs.replicate_id,
        )
        return replace(m, velocity=RunEvalVelocity().compute(m))

    def _cache_breakdown(
        self, i: MetricsInputs,
    ) -> tuple[dict[str, TierCacheStats], float]:
        calc = CacheSavingsCalculator()
        by_tier: dict[str, TierCacheStats] = {}
        savings = 0.0
        for tier, tokens in i.cache_tokens_by_tier.items():
            tier_savings = calc.savings_usd(tokens)
            by_tier[tier] = TierCacheStats(
                create_tokens=tokens.create_tokens,
                read_tokens=tokens.read_tokens,
                savings_usd=tier_savings,
            )
            savings += tier_savings
        return by_tier, savings

    def _structure(self, i: MetricsInputs) -> StructureStats:
        s = i.file_stats
        classes = i.implementation.module.classes
        return StructureStats(
            avg_file_line_count=s.avg_line_count,
            max_file_line_count=s.max_line_count,
            orphan_files=s.orphan_count,
            classes_per_module=(len(classes),),
            max_methods_per_class=max(
                (len(c.methods) for c in classes), default=0,
            ),
            max_args_per_method=max(
                (sig.count(",") + 1 for c in classes for sig in c.methods
                 if "(" in sig and sig.split("(")[1].split(")")[0].strip()),
                default=0,
            ),
        )

    def _reliability(self, i: MetricsInputs) -> ReliabilityStats:
        return ReliabilityStats(
            agent_retries=i.agent_retries,
            agent_hangs=i.llm_timeouts,
            llm_timeouts=i.llm_timeouts,
            classes_fixed=i.classes_fixed,
            fixer_input_tokens=i.fixer_input_tokens,
            fixer_output_tokens=i.fixer_output_tokens,
            fixer_cost_usd=i.fixer_cost_usd,
            fixer_duration_ms=i.fixer_duration_ms,
        )
