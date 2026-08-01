"""VelocityStats value object: token-throughput derivatives (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VelocityStats:
    """Immutable artifact-size estimate plus derived velocity ratios.

    All fields are derived (tokens over wall-clock or artifact-size over
    output tokens); RunEvalVelocity computes the whole value in one shot
    so the ratios can never drift from their inputs.
    """

    artifact_token_estimate: int = 0
    artifact_to_output_ratio: float = 0.0
    icp_artifact_to_output_ratio: float = 0.0
    output_token_velocity: float = 0.0
    artifact_token_velocity: float = 0.0
    architect_velocity: float = 0.0
    test_architect_velocity: float = 0.0
    icp_velocity: float = 0.0
    icp_throughput_velocity: float = 0.0
