"""Tests for the StructureStats value object."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.structure_stats import StructureStats


def test_defaults_zero_except_normalized_acs() -> None:
    s = StructureStats()
    assert s.avg_file_line_count == 0.0
    assert s.classes_per_module == ()
    assert s.acs_composite == 0.0
    assert s.acs_normalized == 1.0


def test_is_frozen() -> None:
    s = StructureStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.orphan_files = 1  # type: ignore[misc]


def test_classes_per_module_is_a_tuple() -> None:
    s = StructureStats(classes_per_module=(5, 3))
    assert s.classes_per_module == (5, 3)


def test_holds_acs_scores() -> None:
    s = StructureStats(acs_structural=2.0, acs_codegen=1.5, acs_composite=3.1)
    assert s.acs_structural == pytest.approx(2.0)
    assert s.acs_composite == pytest.approx(3.1)
