"""RunEvalMetricsBuilder: compute EvalMetrics from pipeline outputs."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.metrics_inputs import MetricsInputs
from squeaky_clean.application.use_cases.cache_savings_calculator import (
    CacheSavingsCalculator,
    TierCacheTokens,
)
from squeaky_clean.application.use_cases.run_eval_token_mapper import RunEvalTokenMapper
from squeaky_clean.application.use_cases.run_eval_velocity import RunEvalVelocity

_PARALLELISM_LIMIT: int = 4


class RunEvalMetricsBuilder:
    """Derive an EvalMetrics from the outputs of one pipeline run."""

    def build(self, inputs: MetricsInputs) -> EvalMetrics:
        """Return an EvalMetrics computed from ``inputs``."""
        m = self._base(inputs)
        RunEvalTokenMapper().apply(m, inputs)
        self._file_stats(m, inputs)
        self._cache_breakdown(m, inputs)
        RunEvalVelocity().apply(m)
        return m

    def _cache_breakdown(self, m: EvalMetrics, i: MetricsInputs) -> None:
        calc = CacheSavingsCalculator()
        tiers = (
            ("architect", i.cache_create_architect_tokens,
             i.cache_read_architect_tokens, i.architect_model),
            ("manager", i.cache_create_manager_tokens,
             i.cache_read_manager_tokens, i.manager_model),
            ("icp", i.cache_create_icp_tokens,
             i.cache_read_icp_tokens, i.icp_model),
            ("fixer", i.cache_create_fixer_tokens,
             i.cache_read_fixer_tokens, i.fixer_model),
        )
        savings = 0.0
        for name, c, r, model in tiers:
            tok = TierCacheTokens(create_tokens=c, read_tokens=r, model=model)
            setattr(m, f"cache_create_{name}_tokens", c)
            setattr(m, f"cache_read_{name}_tokens", r)
            setattr(m, f"cache_hit_ratio_{name}", calc.hit_ratio(tok))
            tier_savings = calc.savings_usd(tok)
            setattr(m, f"cache_savings_{name}_usd", tier_savings)
            savings += tier_savings
        m.cache_savings_usd = savings

    def _base(self, inputs: MetricsInputs) -> EvalMetrics:
        pr = inputs.test_run_result
        total = pr.passed + pr.failed + pr.errors
        impl = inputs.implementation
        m = EvalMetrics.empty()
        m.tests_pass = (pr.passed / total) if total > 0 else 0.0
        m.architecture_violations = len(inputs.validation.violations)
        m.estimated_cost_usd = (
            inputs.architect_cost_usd
            + inputs.test_architect_cost_usd
            + inputs.icp_cost_usd
            + inputs.security_architect_cost_usd
            + inputs.fixer_cost_usd
        )
        m.total_wall_clock_ms = impl.total_duration_ms
        m.parallelism_limit = _PARALLELISM_LIMIT
        m.peak_parallelism = min(len(impl.implemented_classes), _PARALLELISM_LIMIT)
        m.classes_per_module = [len(impl.module.classes)]
        classes = impl.module.classes
        m.max_methods_per_class = max((len(c.methods) for c in classes), default=0)
        m.max_args_per_method = max(
            (s.count(",") + 1 for c in classes for s in c.methods
             if "(" in s and s.split("(")[1].split(")")[0].strip()),
            default=0)
        m.agent_retries = inputs.agent_retries
        m.security_test_count = inputs.security_test_count
        m.cache_hit_count = inputs.cache_hit_count
        m.cache_miss_count = inputs.cache_miss_count
        m.cache_creation_input_tokens = inputs.cache_creation_input_tokens
        m.cache_read_input_tokens = inputs.cache_read_input_tokens
        m.llm_timeouts = inputs.llm_timeouts
        m.replicate_id = inputs.replicate_id
        m.spec_conformance_violations = inputs.spec_conformance_violations
        m.composer_validation_failures = inputs.composer_validation_failures
        m.composer_manager_fallback_calls = inputs.composer_manager_fallback_calls
        self._functional_metrics(m, inputs)
        return m

    def _functional_metrics(
        self, m: EvalMetrics, inputs: MetricsInputs,
    ) -> None:
        fr = inputs.functional_test_run_result
        if fr is not None:
            func_total = fr.passed + fr.failed + fr.errors
            m.functional_tests_pass = (fr.passed / func_total) if func_total > 0 else 0.0
            m.functional_test_count = func_total
            sec_total = (inputs.test_run_result.passed + inputs.test_run_result.failed
                         + inputs.test_run_result.errors) - func_total
            if sec_total > 0:
                sec_passed = inputs.test_run_result.passed - fr.passed
                m.security_tests_pass = (sec_passed / sec_total) if sec_total > 0 else 0.0
        else:
            tr = inputs.test_run_result
            total = tr.passed + tr.failed + tr.errors
            m.functional_tests_pass = m.tests_pass
            m.functional_test_count = total

    def _file_stats(self, m: EvalMetrics, i: MetricsInputs) -> None:
        s = i.file_stats
        m.avg_file_line_count = s.avg_line_count
        m.max_file_line_count = s.max_line_count
        m.orphan_files = s.orphan_count
        art = s.artifact_char_count // 4
        m.artifact_token_estimate = art
        out = m.total_tokens_output
        icp_out = i.icp_output_tokens
        m.artifact_to_output_ratio = (art / out) if out > 0 else 0.0
        m.icp_artifact_to_output_ratio = (art / icp_out) if icp_out > 0 else 0.0
