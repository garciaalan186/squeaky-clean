"""ComposerStats DTO: telemetry counters for TechSpecComposer (H2)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ComposerStats:
    """Per-run TechSpecComposer telemetry surfaced into EvalMetrics."""

    validation_failures: int = 0
    manager_fallback_calls: int = 0
    manager_corrections_accepted: int = 0
