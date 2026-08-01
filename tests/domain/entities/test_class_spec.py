"""Tests for ClassSpec."""

import dataclasses

import pytest

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.class_role import ClassRole


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


def _spec(
    implements: str | None = None,
    depends: tuple[str, ...] = (),
    concretes: tuple[str, ...] = (),
    fields: tuple[str, ...] = (),
) -> ClassSpec:
    return ClassSpec(
        name="A", pattern="Strategy", implements=implements,
        methods=(), depends=depends, concretes=concretes, fields=fields,
    )


def test_role_abstract_when_concretes_declared() -> None:
    assert _spec(concretes=("B", "C")).role() is ClassRole.ABSTRACT


def test_role_abstract_wins_over_implements() -> None:
    assert _spec(implements="P", concretes=("B",)).role() is ClassRole.ABSTRACT


def test_role_concrete_when_implements_set() -> None:
    assert _spec(implements="P").role() is ClassRole.CONCRETE


def test_role_plain_otherwise() -> None:
    assert _spec().role() is ClassRole.PLAIN


def test_unknown_dep_violations_flags_unresolvable() -> None:
    spec = _spec(depends=("Known", "Ghost"))
    assert spec.unknown_dep_violations({"Known"}) == [
        "A depends on unknown class Ghost",
    ]


def test_unknown_dep_violations_resolves_qualified_by_bare_name() -> None:
    spec = _spec(depends=("Mod::Known",))
    assert spec.unknown_dep_violations({"Known"}) == []


def test_field_syntax_violations_flags_missing_colon() -> None:
    spec = _spec(fields=("ok: Type", "broken"))
    assert spec.field_syntax_violations() == [
        "A field 'broken' missing 'name: Type'",
    ]
