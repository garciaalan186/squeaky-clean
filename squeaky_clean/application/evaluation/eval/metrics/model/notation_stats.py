"""NotationStats value object: spec/notation conformance counters (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NotationStats:
    """Immutable notation-conformance and infrastructure-choice counters.

    Groups the counters that measure how faithfully the generated system
    followed its Squib: conformance/obligation gaps, convention
    violations, composer fallbacks, and the infrastructure-choice (MCDA)
    telemetry.
    """

    notation_novelty: int = 0
    spec_conformance_violations: int = 0
    test_obligation_gaps: int = 0
    cross_module_dependency_violations: int = 0
    http_convention_violations: int = 0
    dependency_injection_violations: int = 0
    test_criteria_filtered: int = 0
    composer_validation_failures: int = 0
    composer_manager_fallback_calls: int = 0
    infrastructure_choices_explicit: int = 0
    infrastructure_choices_derived: int = 0
    infrastructure_icp_count: int = 0
    mcda_runs: int = 0
    dependency_install_failed: bool = False
