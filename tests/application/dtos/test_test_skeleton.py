"""Tests for TestSkeleton DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.test_skeleton import TestSkeleton


def test_construction_preserves_fields() -> None:
    skel = TestSkeleton(
        class_name="Operand",
        file_path="tests/test_operand.py",
        code="import pytest\n\ndef test_value() -> None:\n    pytest.fail('x')\n",
    )
    assert skel.class_name == "Operand"
    assert skel.file_path == "tests/test_operand.py"
    assert "pytest.fail" in skel.code


def test_frozen_behavior() -> None:
    skel = TestSkeleton(class_name="A", file_path="tests/test_a.py", code="")
    with pytest.raises(FrozenInstanceError):
        skel.class_name = "B"  # type: ignore[misc]
