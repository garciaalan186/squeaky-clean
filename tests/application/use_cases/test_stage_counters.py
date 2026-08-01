"""Tests for StageCounters: frozen per-stage tallies (R6.2)."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.run.stages.stage_counters import StageCounters


def test_defaults_are_all_zero_or_false() -> None:
    c = StageCounters()
    assert c.di_violations == 0
    assert c.architect_retries == 0
    assert c.http_violations == 0
    assert c.notation_novelty == 0
    assert c.test_criteria_filtered == 0
    assert c.infra_explicit == 0
    assert c.infra_derived == 0
    assert c.mcda_runs == 0
    assert c.dep_install_failed is False


def test_is_frozen() -> None:
    c = StageCounters()
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.di_violations = 3  # type: ignore[misc]


def test_replace_returns_updated_copy_without_mutating_original() -> None:
    original = StageCounters()
    updated = dataclasses.replace(
        original, http_violations=4, dep_install_failed=True,
    )
    assert updated is not original
    assert updated.http_violations == 4
    assert updated.dep_install_failed is True
    assert original.http_violations == 0
    assert original.dep_install_failed is False
    # Untouched fields are carried over verbatim.
    assert updated.architect_retries == original.architect_retries
