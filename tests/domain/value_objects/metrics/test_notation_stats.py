"""Tests for the NotationStats value object."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.notation_stats import NotationStats


def test_defaults_are_zero() -> None:
    n = NotationStats()
    assert n.notation_novelty == 0
    assert n.spec_conformance_violations == 0
    assert n.mcda_runs == 0
    assert n.dependency_install_failed is False


def test_is_frozen() -> None:
    n = NotationStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        n.mcda_runs = 1  # type: ignore[misc]


def test_holds_conformance_counters() -> None:
    n = NotationStats(
        spec_conformance_violations=2, test_obligation_gaps=1,
        http_convention_violations=3, infrastructure_icp_count=4,
        dependency_install_failed=True,
    )
    assert n.spec_conformance_violations == 2
    assert n.infrastructure_icp_count == 4
    assert n.dependency_install_failed is True
