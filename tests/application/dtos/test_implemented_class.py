"""Tests for ImplementedClass DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.implemented_class import ImplementedClass


def test_construction_preserves_fields() -> None:
    ic = ImplementedClass(
        class_name="Operand",
        file_path="src/operand.py",
        code="class Operand: pass",
        test_code=None,
        cost_usd=0.01,
        duration_ms=1234,
        input_tokens=100,
        output_tokens=50,
    )
    assert ic.class_name == "Operand"
    assert ic.test_code is None
    assert ic.cost_usd == 0.01
    assert ic.duration_ms == 1234
    assert ic.input_tokens == 100
    assert ic.output_tokens == 50


def test_frozen_behavior() -> None:
    ic = ImplementedClass(
        class_name="A",
        file_path="src/a.py",
        code="class A: pass",
        test_code=None,
        cost_usd=0.0,
        duration_ms=0,
        input_tokens=0,
        output_tokens=0,
    )
    with pytest.raises(FrozenInstanceError):
        ic.class_name = "B"  # type: ignore[misc]
