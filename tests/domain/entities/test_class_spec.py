"""Tests for ClassSpec."""

import dataclasses

import pytest

from squeaky_clean.domain.entities.class_spec import ClassSpec


def test_class_spec_fields_roundtrip() -> None:
    spec = ClassSpec(
        name="PaymentService",
        pattern="Facade",
        implements=None,
        methods=("process(command: Cmd): Result",),
        depends=("PaymentRepository",),
        concretes=(),
    )
    assert spec.name == "PaymentService"
    assert spec.pattern == "Facade"
    assert spec.methods == ("process(command: Cmd): Result",)
    assert spec.fields == ()


def test_class_spec_accepts_fields_entry() -> None:
    spec = ClassSpec(
        name="Todo",
        pattern="Entity",
        implements=None,
        methods=("mark_complete(): None",),
        depends=(),
        concretes=(),
        fields=("id: TodoId", "title: TodoTitle"),
    )
    assert spec.fields == ("id: TodoId", "title: TodoTitle")


def test_class_spec_is_frozen() -> None:
    spec = ClassSpec(
        name="A",
        pattern="SimpleClass",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(spec, "name", "B")  # noqa: B010


def test_class_spec_accepts_invariants_entry() -> None:
    spec = ClassSpec(
        name="TodoTitle",
        pattern="ValueObject",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
        fields=("value: str",),
        invariants=("title must be non-empty",),
    )
    assert spec.invariants == ("title must be non-empty",)


def test_class_spec_defaults_invariants_to_empty() -> None:
    spec = ClassSpec(
        name="A",
        pattern="SimpleClass",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
    )
    assert spec.invariants == ()
