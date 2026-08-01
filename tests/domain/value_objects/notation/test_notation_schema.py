"""Tests for NotationSchema / SQUIB_SCHEMA — the grammar as data (R6.1c)."""

from pathlib import Path

import pytest

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.notation.notation_schema import SQUIB_SCHEMA


def test_singleton_sections_are_module_and_layer() -> None:
    assert SQUIB_SCHEMA.singleton_sections() == frozenset({"MODULE", "LAYER"})


def test_required_sections_in_declaration_order() -> None:
    names = [s.name for s in SQUIB_SCHEMA.required_sections()]
    assert names == ["MODULE", "LAYER", "CLASSES"]


def test_class_field_order_is_the_shape_signature_order() -> None:
    # Bit order of R5.5 novelty signatures — changing this breaks signature
    # comparability across runs and triage snapshots. Deliberate change only.
    assert SQUIB_SCHEMA.class_field_names() == (
        "fields", "methods", "depends", "concretes", "implements", "invariants",
    )


def test_unknown_names_raise_key_error() -> None:
    with pytest.raises(KeyError):
        SQUIB_SCHEMA.section("NOPE")
    with pytest.raises(KeyError):
        SQUIB_SCHEMA.class_field("nope")


def test_class_spec_presence_keys_match_schema() -> None:
    spec = ClassSpec(
        name="Payment", pattern="Entity", implements=None,
        methods=("validate(): Result",), depends=(), concretes=(),
    )
    assert set(spec.notation_presence()) == set(SQUIB_SCHEMA.class_field_names())


def test_squib_doc_names_every_grammar_row() -> None:
    # Drift guard: the hand-maintained grammar reference must mention every
    # section and class field the schema declares.
    doc = (
        Path(__file__).resolve().parents[4] / "docs" / "squib.md"
    ).read_text()
    for section in SQUIB_SCHEMA.sections:
        assert section.name in doc, f"docs/squib.md missing section {section.name}"
    for class_field in SQUIB_SCHEMA.class_fields:
        assert f"`{class_field.name}:`" in doc, (
            f"docs/squib.md missing class field {class_field.name}"
        )
