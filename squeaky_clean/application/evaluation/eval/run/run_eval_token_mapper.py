"""RunEvalTokenMapper: build the CostBreakdown VO from MetricsInputs."""

from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown


class RunEvalTokenMapper:
    """Maps per-agent token counts and costs into one frozen CostBreakdown."""

    def map(self, i: MetricsInputs) -> CostBreakdown:
        """Return the CostBreakdown for ``i`` (fixer cost included in total)."""
        return CostBreakdown(
            estimated_cost_usd=(
                i.architect_cost_usd + i.test_architect_cost_usd
                + i.icp_cost_usd + i.security_architect_cost_usd
                + i.fixer_cost_usd
            ),
            total_tokens_input=(
                i.architect_input_tokens + i.test_architect_input_tokens
                + i.icp_input_tokens + i.security_architect_input_tokens
                + i.fixer_input_tokens
            ),
            total_tokens_output=(
                i.architect_output_tokens + i.test_architect_output_tokens
                + i.icp_output_tokens + i.security_architect_output_tokens
                + i.fixer_output_tokens
            ),
            architect_input_tokens=i.architect_input_tokens,
            architect_output_tokens=i.architect_output_tokens,
            architect_cost_usd=i.architect_cost_usd,
            architect_duration_ms=i.architect_duration_ms,
            test_architect_input_tokens=i.test_architect_input_tokens,
            test_architect_output_tokens=i.test_architect_output_tokens,
            test_architect_cost_usd=i.test_architect_cost_usd,
            test_architect_duration_ms=i.test_architect_duration_ms,
            icp_input_tokens=i.icp_input_tokens,
            icp_output_tokens=i.icp_output_tokens,
            icp_cost_usd=i.icp_cost_usd,
            icp_duration_ms=i.icp_duration_ms,
            icp_wall_duration_ms=i.icp_wall_duration_ms,
            security_architect_input_tokens=i.security_architect_input_tokens,
            security_architect_output_tokens=i.security_architect_output_tokens,
            security_architect_cost_usd=i.security_architect_cost_usd,
            security_architect_duration_ms=i.security_architect_duration_ms,
        )
