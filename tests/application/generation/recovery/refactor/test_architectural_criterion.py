"""Tests for ArchitecturalCriterion: the shared trade-off criteria literal."""

from typing import get_args

from squeaky_clean.application.generation.recovery.refactor.architectural_criterion import (
    ALL_ARCHITECTURAL_CRITERIA,
    ArchitecturalCriterion,
)


def test_all_criteria_mirror_the_literal_in_declaration_order() -> None:
    assert ALL_ARCHITECTURAL_CRITERIA == tuple(get_args(ArchitecturalCriterion))


def test_the_six_expected_criteria_are_declared() -> None:
    assert ALL_ARCHITECTURAL_CRITERIA == (
        "testability", "simplicity", "performance",
        "evolvability", "migration_safety", "delivery_speed",
    )


def test_criteria_names_are_unique() -> None:
    assert len(set(ALL_ARCHITECTURAL_CRITERIA)) == len(ALL_ARCHITECTURAL_CRITERIA)
