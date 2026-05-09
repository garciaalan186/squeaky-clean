"""Tests for TestArchitecture DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton


def test_construction_preserves_fields() -> None:
    skel = TestSkeleton(
        class_name="Calculator",
        file_path="tests/test_calculator.py",
        code="import pytest\n",
    )
    ta = TestArchitecture(
        gherkin_scenarios=("Feature: X\nScenario: Y\nGiven a\nWhen b\nThen c",),
        test_skeletons=(skel,),
    )
    assert ta.gherkin_scenarios[0].startswith("Feature: X")
    assert ta.test_skeletons[0].class_name == "Calculator"


def test_frozen_behavior() -> None:
    ta = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    with pytest.raises(FrozenInstanceError):
        ta.gherkin_scenarios = ("new",)  # type: ignore[misc]
