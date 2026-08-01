"""Tests for RecoverySummary: what a front-half recovery run reports."""

import dataclasses

import pytest

from squeaky_clean.application.generation.recovery.refactor.recovery_summary import (
    RecoverySummary,
)


def _summary() -> RecoverySummary:
    return RecoverySummary(
        classes=12, modules=3, violations=7, coupling_violations=2,
        recommendation="split", recommendation_close=False,
        squib_path="out/squib.txt", violations_path="out/violations.json",
    )


def test_summary_carries_counts_verdict_and_output_paths() -> None:
    summary = _summary()
    assert (summary.classes, summary.modules) == (12, 3)
    assert summary.coupling_violations <= summary.violations
    assert summary.recommendation == "split"
    assert summary.squib_path == "out/squib.txt"
    assert summary.violations_path == "out/violations.json"


def test_identical_summaries_compare_equal() -> None:
    assert _summary() == _summary()
    assert _summary() != dataclasses.replace(_summary(), recommendation_close=True)


def test_summary_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(_summary(), "violations", 0)  # noqa: B010
