"""ReliabilityStats value object: retry/timeout/repair counters (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReliabilityStats:
    """Immutable reliability counters: retries, hangs, and repair telemetry.

    ``agent_hangs`` mirrors ``llm_timeouts`` (a hang is recorded per
    timeout). Fixer token/cost counters live here with ``classes_fixed``
    and ``compile_errors`` because they measure repair work, not planned
    generation spend (which is CostBreakdown's concern) — the fixer's
    cost still folds into ``CostBreakdown.estimated_cost_usd``.
    """

    agent_retries: int = 0
    agent_hangs: int = 0
    hallucinations: int = 0
    llm_timeouts: int = 0
    architect_retries: int = 0
    compile_errors: int = 0
    classes_fixed: int = 0
    fixer_input_tokens: int = 0
    fixer_output_tokens: int = 0
    fixer_cost_usd: float = 0.0
    fixer_duration_ms: int = 0
