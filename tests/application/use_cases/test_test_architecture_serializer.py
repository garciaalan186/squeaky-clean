"""Tests for TestArchitectureSerializer round-trip (G3)."""

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton
from squeaky_clean.application.use_cases.test_architecture_serializer import (
    TestArchitectureSerializer,
)


def _arch() -> TestArchitecture:
    sk = TestSkeleton(
        class_name="Add", file_path="tests/test_add.py",
        code="def test_add(): pass\n",
    )
    return TestArchitecture(
        gherkin_scenarios=("Feature: Add\n  Scenario: 1+1=2",),
        test_skeletons=(sk,),
    )


def test_round_trip_preserves_equality() -> None:
    arch = _arch()
    ser = TestArchitectureSerializer()
    assert ser.deserialize(ser.serialize(arch)) == arch


def test_empty_round_trip() -> None:
    arch = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    ser = TestArchitectureSerializer()
    assert ser.deserialize(ser.serialize(arch)) == arch
