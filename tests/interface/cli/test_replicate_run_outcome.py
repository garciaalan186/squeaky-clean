"""Tests for ReplicateRunOutcome DTO."""

from pathlib import Path

from squeaky_clean.interface.cli.replicates.replicate_run_outcome import ReplicateRunOutcome


def test_frozen_fields() -> None:
    outcome = ReplicateRunOutcome(summary_path=Path("/x/s.json"), runs=3)
    assert outcome.runs == 3 and outcome.summary_path.name == "s.json"
