"""RunEvalVelocity: compute token velocity metrics on a populated EvalMetrics."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics


class RunEvalVelocity:
    """Derives per-agent and aggregate velocity from wall-clock time."""

    def apply(self, m: EvalMetrics) -> None:
        """Set velocity fields on ``m`` in place."""
        secs = m.total_wall_clock_ms / 1000.0
        if secs > 0:
            m.output_token_velocity = m.total_tokens_output / secs
            m.artifact_token_velocity = m.artifact_token_estimate / secs
        m.architect_velocity = self._v(
            m.architect_output_tokens, m.architect_duration_ms
        )
        m.test_architect_velocity = self._v(
            m.test_architect_output_tokens, m.test_architect_duration_ms
        )
        m.icp_velocity = self._v(
            m.icp_output_tokens, m.icp_duration_ms
        )
        m.icp_throughput_velocity = self._v(
            m.icp_output_tokens, m.icp_wall_duration_ms
        )

    def _v(self, tokens: int, ms: int) -> float:
        return (tokens / (ms / 1000.0)) if ms > 0 else 0.0
