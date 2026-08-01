"""MetricsInputs DTO: inputs to RunEvalMetricsBuilder.build()."""

from dataclasses import dataclass, field

from squeaky_clean.application.evaluation.eval.metrics.cache_savings_calculator import (
    TierCacheTokens,
)
from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


@dataclass(frozen=True)
class MetricsInputs:
    """Immutable bundle of pipeline outputs used to build an EvalMetrics.

    Bundling the pipeline outputs onto one DTO lets
    ``RunEvalMetricsBuilder.build`` take exactly one argument, which
    respects the hard <=2-args rule.
    """

    implementation: ModuleImplementation
    test_run_result: TestRunResult
    validation: ValidationReport
    architect_input_tokens: int
    architect_output_tokens: int
    architect_cost_usd: float
    architect_duration_ms: int
    test_architect_input_tokens: int
    test_architect_output_tokens: int
    test_architect_cost_usd: float
    test_architect_duration_ms: int
    icp_input_tokens: int
    icp_output_tokens: int
    icp_cost_usd: float
    icp_duration_ms: int
    icp_wall_duration_ms: int
    file_stats: FileStats
    functional_test_run_result: TestRunResult | None = None
    agent_retries: int = 0
    security_test_count: int = 0
    security_architect_input_tokens: int = 0
    security_architect_output_tokens: int = 0
    security_architect_cost_usd: float = 0.0
    security_architect_duration_ms: int = 0
    classes_fixed: int = 0
    fixer_input_tokens: int = 0
    fixer_output_tokens: int = 0
    fixer_cost_usd: float = 0.0
    fixer_duration_ms: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    llm_timeouts: int = 0
    replicate_id: int = 0
    spec_conformance_violations: int = 0
    # Per-tier cache token totals + routed model, keyed by ModelTier.value.
    cache_tokens_by_tier: dict[str, TierCacheTokens] = field(default_factory=dict)
    composer_validation_failures: int = 0
    composer_manager_fallback_calls: int = 0
    wall_clock_ms: int = 0
