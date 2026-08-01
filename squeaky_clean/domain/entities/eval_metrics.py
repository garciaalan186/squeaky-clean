"""EvalMetrics: frozen aggregate of one eval run's metric groups (R6.3).

Formerly a ~90-field mutable dataclass; now composed of seven frozen
value objects plus a handful of loose run-level fields. Builders return
values (or ``dataclasses.replace`` on frozen copies) instead of mutating.

Property passthroughs (hot fields, preserved top-level access paths):
``tests_pass``, ``functional_tests_pass``, ``security_tests_pass``,
``estimated_cost_usd``. Capped at four so the class stays within the
<=5-public-methods granularity rule alongside ``empty()``;
``architecture_violations`` and ``total_wall_clock_ms`` remain loose
fields for the same reason. Every other former flat field is reached
through its value object (e.g. ``m.test_outcome.test_status``).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.domain.value_objects.metrics.notation_stats import NotationStats
from squeaky_clean.domain.value_objects.metrics.reliability_stats import ReliabilityStats
from squeaky_clean.domain.value_objects.metrics.security_scan_stats import SecurityScanStats
from squeaky_clean.domain.value_objects.metrics.structure_stats import StructureStats
from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome
from squeaky_clean.domain.value_objects.metrics.tier_cache_stats import TierCacheStats
from squeaky_clean.domain.value_objects.metrics.velocity_stats import VelocityStats


@dataclass(frozen=True)
class EvalMetrics:
    """Frozen aggregate of metrics collected during one eval run."""

    test_outcome: TestOutcome = field(default_factory=TestOutcome)
    cost: CostBreakdown = field(default_factory=CostBreakdown)
    velocity: VelocityStats = field(default_factory=VelocityStats)
    structure: StructureStats = field(default_factory=StructureStats)
    reliability: ReliabilityStats = field(default_factory=ReliabilityStats)
    notation: NotationStats = field(default_factory=NotationStats)
    security_scan: SecurityScanStats = field(default_factory=SecurityScanStats)

    architecture_violations: int = 0
    total_wall_clock_ms: int = 0
    parallelism_limit: int = 0
    peak_parallelism: int = 0

    # Per-tier cache breakdown, keyed by ModelTier.value ("architect", ...).
    cache_by_tier: dict[str, TierCacheStats] = field(default_factory=dict)
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0
    cache_savings_usd: float = 0.0

    replicate_id: int = 0
    runs: int = 1
    budget_exceeded: bool = False

    @classmethod
    def empty(cls) -> EvalMetrics:
        """Return a fresh zero-initialized EvalMetrics instance."""
        return cls()

    @property
    def tests_pass(self) -> float:
        """Passthrough: headline pass rate (test_outcome.tests_pass)."""
        return self.test_outcome.tests_pass

    @property
    def functional_tests_pass(self) -> float:
        """Passthrough: test_outcome.functional_tests_pass."""
        return self.test_outcome.functional_tests_pass

    @property
    def security_tests_pass(self) -> float:
        """Passthrough: test_outcome.security_tests_pass."""
        return self.test_outcome.security_tests_pass

    @property
    def estimated_cost_usd(self) -> float:
        """Passthrough: cost.estimated_cost_usd."""
        return self.cost.estimated_cost_usd
