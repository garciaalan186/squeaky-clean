"""RunMetricsSnapshot DTO: one meta-eval run's flattened numeric metrics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunMetricsSnapshot:
    """Immutable snapshot of one meta-eval run's metrics.json + identity.

    ``run_number`` is the zero-padded NNN extracted from the directory
    name. ``timestamp`` is the YYYYMMDD-HHMMSS suffix. ``metrics`` is
    the loaded metrics dict flattened to numeric scalars only — list,
    bool, and string fields are dropped. ``problem_id`` is derived from
    the run's first ``problem-set-*-code`` subdirectory; empty when no
    such subdirectory exists.
    """

    run_number: int
    timestamp: str
    metrics: dict[str, float | int]
    problem_id: str
