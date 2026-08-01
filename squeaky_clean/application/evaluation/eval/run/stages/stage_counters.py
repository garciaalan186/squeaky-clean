"""StageCounters: frozen tallies stages report instead of pipeline mutables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageCounters:
    """What used to be 11 mutable attributes on the god-orchestrator (R6.2).

    Stages return updated copies via ``dataclasses.replace`` (fully typed);
    the metrics stage folds the final values into EvalMetrics. Frozen so a
    stage cannot silently mutate another stage's tally.
    """

    di_violations: int = 0
    architect_retries: int = 0
    http_violations: int = 0
    notation_novelty: int = 0
    test_criteria_filtered: int = 0
    infra_explicit: int = 0
    infra_derived: int = 0
    mcda_runs: int = 0
    dep_install_failed: bool = False
