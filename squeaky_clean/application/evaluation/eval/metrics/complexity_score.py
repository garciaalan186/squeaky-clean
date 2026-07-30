"""ComplexityScore DTO: per-run Architectural Complexity Score (ACS).

See BENCHMARK_METHODOLOGY.md for the full methodology and weight defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComplexityScore:
    """Composite complexity metric with three independent dimensions."""

    structural: float = 0.0       # S — pre-codegen architecture breadth
    codegen: float = 0.0          # G — post-codegen AST + SDK surface
    constraint: float = 0.0       # P — ProblemSpec constraint surface
    composite: float = 0.0        # weighted sum (ACS)
    normalized: float = 1.0       # ACS / ACS_baseline (P0 Calculator)
    components: dict[str, float] = field(default_factory=dict)
