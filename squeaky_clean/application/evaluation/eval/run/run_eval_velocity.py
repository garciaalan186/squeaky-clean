"""RunEvalVelocity: derive the full VelocityStats VO from an EvalMetrics."""

from dataclasses import replace

from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.velocity_stats import VelocityStats


class RunEvalVelocity:
    """Derives velocity/ratio fields from cost, wall-clock, and artifact size.

    Reads ``m.velocity.artifact_token_estimate`` (pre-seeded by the
    builder) plus ``m.cost`` and ``m.total_wall_clock_ms``; returns a
    complete VelocityStats in one shot so ratios can never drift.
    """

    def compute(self, m: EvalMetrics) -> VelocityStats:
        """Return the fully-derived VelocityStats for ``m``."""
        art = m.velocity.artifact_token_estimate
        out = m.cost.total_tokens_output
        icp_out = m.cost.icp_output_tokens
        secs = m.total_wall_clock_ms / 1000.0
        return replace(
            m.velocity,
            artifact_to_output_ratio=(art / out) if out > 0 else 0.0,
            icp_artifact_to_output_ratio=(art / icp_out) if icp_out > 0 else 0.0,
            output_token_velocity=(out / secs) if secs > 0 else 0.0,
            artifact_token_velocity=(art / secs) if secs > 0 else 0.0,
            architect_velocity=self._v(
                m.cost.architect_output_tokens, m.cost.architect_duration_ms,
            ),
            test_architect_velocity=self._v(
                m.cost.test_architect_output_tokens,
                m.cost.test_architect_duration_ms,
            ),
            icp_velocity=self._v(icp_out, m.cost.icp_duration_ms),
            icp_throughput_velocity=self._v(
                icp_out, m.cost.icp_wall_duration_ms,
            ),
        )

    def _v(self, tokens: int, ms: int) -> float:
        return (tokens / (ms / 1000.0)) if ms > 0 else 0.0
