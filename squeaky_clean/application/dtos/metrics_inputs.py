"""MetricsInputs DTO: inputs to RunEvalMetricsBuilder.build()."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.file_stats import FileStats
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport


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
    cache_create_architect_tokens: int = 0
    cache_read_architect_tokens: int = 0
    cache_create_manager_tokens: int = 0
    cache_read_manager_tokens: int = 0
    cache_create_icp_tokens: int = 0
    cache_read_icp_tokens: int = 0
    cache_create_fixer_tokens: int = 0
    cache_read_fixer_tokens: int = 0
    architect_model: str = ""
    manager_model: str = ""
    icp_model: str = ""
    fixer_model: str = ""
    composer_validation_failures: int = 0
    composer_manager_fallback_calls: int = 0
