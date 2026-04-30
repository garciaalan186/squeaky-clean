"""RunEvalTokenMapper: copy token/cost fields from MetricsInputs to EvalMetrics."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.metrics_inputs import MetricsInputs


class RunEvalTokenMapper:
    """Maps token-count and cost fields from pipeline inputs to metrics."""

    def apply(self, m: EvalMetrics, i: MetricsInputs) -> None:
        """Copy per-agent token counts and costs onto ``m``."""
        m.architect_input_tokens = i.architect_input_tokens
        m.architect_output_tokens = i.architect_output_tokens
        m.architect_cost_usd = i.architect_cost_usd
        m.architect_duration_ms = i.architect_duration_ms
        m.test_architect_input_tokens = i.test_architect_input_tokens
        m.test_architect_output_tokens = i.test_architect_output_tokens
        m.test_architect_cost_usd = i.test_architect_cost_usd
        m.test_architect_duration_ms = i.test_architect_duration_ms
        m.icp_input_tokens = i.icp_input_tokens
        m.icp_output_tokens = i.icp_output_tokens
        m.icp_cost_usd = i.icp_cost_usd
        m.icp_duration_ms = i.icp_duration_ms
        m.icp_wall_duration_ms = i.icp_wall_duration_ms
        m.security_architect_input_tokens = i.security_architect_input_tokens
        m.security_architect_output_tokens = i.security_architect_output_tokens
        m.security_architect_cost_usd = i.security_architect_cost_usd
        m.security_architect_duration_ms = i.security_architect_duration_ms
        m.classes_fixed = i.classes_fixed
        m.fixer_input_tokens = i.fixer_input_tokens
        m.fixer_output_tokens = i.fixer_output_tokens
        m.fixer_cost_usd = i.fixer_cost_usd
        m.fixer_duration_ms = i.fixer_duration_ms
        m.total_tokens_input = (
            i.architect_input_tokens + i.test_architect_input_tokens
            + i.icp_input_tokens + i.security_architect_input_tokens
            + i.fixer_input_tokens
        )
        m.total_tokens_output = (
            i.architect_output_tokens + i.test_architect_output_tokens
            + i.icp_output_tokens + i.security_architect_output_tokens
            + i.fixer_output_tokens
        )
