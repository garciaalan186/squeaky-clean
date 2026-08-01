"""Tests for ClassSpecBuilder: ClassRecord -> Squib ClassSpec mapping."""

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.extraction.class_spec_builder import (
    ClassSpecBuilder,
)


def _record(fields: tuple[str, ...] = ()) -> ClassRecord:
    return ClassRecord(
        fqn="proj.domain.order.Order",
        bases=(),
        methods=("total()",),
        fields=fields,
        imports=(),
        decorators=(),
    )


def test_name_is_the_last_fqn_segment_and_pattern_defaults_to_simple_class() -> None:
    spec = ClassSpecBuilder().build(_record(), depends=())
    assert spec.name == "Order"
    assert spec.pattern == "SimpleClass"
    assert spec.methods == ("total()",)


def test_untyped_fields_gain_object_annotation_typed_pass_through() -> None:
    spec = ClassSpecBuilder().build(
        _record(fields=("total", "name: str")), depends=(),
    )
    assert spec.fields == ("total: object", "name: str")


def test_depends_and_explicit_pattern_are_carried_verbatim() -> None:
    spec = ClassSpecBuilder().build(
        _record(), depends=("LineItem",), pattern="Entity",
    )
    assert spec.depends == ("LineItem",)
    assert spec.pattern == "Entity"
    assert spec.concretes == ()
    assert spec.invariants == ()
