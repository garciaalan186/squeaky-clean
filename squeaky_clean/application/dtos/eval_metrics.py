"""EvalMetrics DTO: mutable aggregated metrics for one eval run."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvalMetrics:
    """Aggregated metrics collected during one Squeaky Clean eval run."""

    tests_pass: float = 0.0
    architecture_violations: int = 0
    compile_errors: int = 0

    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_wall_clock_ms: int = 0
    parallelism_limit: int = 0
    peak_parallelism: int = 0

    avg_file_line_count: float = 0.0
    max_file_line_count: int = 0
    max_methods_per_class: int = 0
    max_args_per_method: int = 0
    classes_per_module: list[int] = field(default_factory=list)
    orphan_files: int = 0

    agent_retries: int = 0
    agent_hangs: int = 0
    hallucinations: int = 0

    estimated_cost_usd: float = 0.0

    architect_input_tokens: int = 0
    architect_output_tokens: int = 0
    test_architect_input_tokens: int = 0
    test_architect_output_tokens: int = 0
    icp_input_tokens: int = 0
    icp_output_tokens: int = 0

    architect_cost_usd: float = 0.0
    test_architect_cost_usd: float = 0.0
    icp_cost_usd: float = 0.0
    architect_duration_ms: int = 0
    test_architect_duration_ms: int = 0
    icp_duration_ms: int = 0

    icp_wall_duration_ms: int = 0

    artifact_token_estimate: int = 0
    artifact_to_output_ratio: float = 0.0
    icp_artifact_to_output_ratio: float = 0.0
    output_token_velocity: float = 0.0
    artifact_token_velocity: float = 0.0
    architect_velocity: float = 0.0
    test_architect_velocity: float = 0.0
    icp_velocity: float = 0.0
    icp_throughput_velocity: float = 0.0

    functional_test_count: int = 0
    functional_tests_pass: float = 0.0
    security_test_count: int = 0
    security_tests_pass: float = 0.0
    security_architect_input_tokens: int = 0
    security_architect_output_tokens: int = 0
    security_architect_cost_usd: float = 0.0
    security_architect_duration_ms: int = 0

    classes_fixed: int = 0
    fixer_input_tokens: int = 0
    fixer_output_tokens: int = 0
    fixer_cost_usd: float = 0.0
    fixer_duration_ms: int = 0

    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0
    llm_timeouts: int = 0

    cache_create_architect_tokens: int = 0
    cache_read_architect_tokens: int = 0
    cache_create_manager_tokens: int = 0
    cache_read_manager_tokens: int = 0
    cache_create_icp_tokens: int = 0
    cache_read_icp_tokens: int = 0
    cache_create_fixer_tokens: int = 0
    cache_read_fixer_tokens: int = 0
    cache_hit_ratio_architect: float = 0.0
    cache_hit_ratio_manager: float = 0.0
    cache_hit_ratio_icp: float = 0.0
    cache_hit_ratio_fixer: float = 0.0
    cache_savings_architect_usd: float = 0.0
    cache_savings_manager_usd: float = 0.0
    cache_savings_icp_usd: float = 0.0
    cache_savings_fixer_usd: float = 0.0
    cache_savings_usd: float = 0.0
    # Architectural Complexity Score (ACS) — see BENCHMARK_METHODOLOGY.md.
    acs_structural: float = 0.0
    acs_codegen: float = 0.0
    acs_constraint: float = 0.0
    acs_composite: float = 0.0
    acs_normalized: float = 1.0
    acs_cost_per_unit: float = 0.0
    acs_velocity: float = 0.0

    replicate_id: int = 0
    runs: int = 1

    spec_conformance_violations: int = 0
    cross_module_dependency_violations: int = 0
    http_convention_violations: int = 0
    architect_retries: int = 0

    budget_exceeded: bool = False

    secret_leaks_detected: int = 0
    sast_high_findings: int = 0
    sast_medium_findings: int = 0
    sast_failed: bool = False

    composer_validation_failures: int = 0
    composer_manager_fallback_calls: int = 0

    infrastructure_choices_explicit: int = 0
    infrastructure_choices_derived: int = 0
    infrastructure_icp_count: int = 0
    mcda_runs: int = 0

    dependency_install_failed: bool = False

    test_criteria_filtered: int = 0

    @classmethod
    def empty(cls) -> EvalMetrics:
        """Return a fresh zero-initialized EvalMetrics instance."""
        return cls()
