"""CostBreakdown value object: per-tier token/cost/duration totals (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostBreakdown:
    """Immutable per-agent token counts, USD costs, and durations.

    ``estimated_cost_usd`` is the run headline: the sum of every tier's
    cost including the fixer (whose token counters live on
    ReliabilityStats with the other repair telemetry). ``total_tokens_*``
    aggregate across all tiers.
    """

    estimated_cost_usd: float = 0.0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    architect_input_tokens: int = 0
    architect_output_tokens: int = 0
    architect_cost_usd: float = 0.0
    architect_duration_ms: int = 0
    test_architect_input_tokens: int = 0
    test_architect_output_tokens: int = 0
    test_architect_cost_usd: float = 0.0
    test_architect_duration_ms: int = 0
    icp_input_tokens: int = 0
    icp_output_tokens: int = 0
    icp_cost_usd: float = 0.0
    icp_duration_ms: int = 0
    icp_wall_duration_ms: int = 0
    security_architect_input_tokens: int = 0
    security_architect_output_tokens: int = 0
    security_architect_cost_usd: float = 0.0
    security_architect_duration_ms: int = 0
