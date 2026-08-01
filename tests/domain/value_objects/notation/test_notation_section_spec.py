"""Tests for NotationSectionSpec grammar rows."""

from squeaky_clean.domain.value_objects.notation.notation_section_spec import NotationSectionSpec


def test_missing_message_scalar_says_declaration() -> None:
    spec = NotationSectionSpec("MODULE", "scalar", required=True, singleton=True)
    assert spec.missing_message() == "missing MODULE declaration"


def test_missing_message_classes_says_block() -> None:
    spec = NotationSectionSpec("CLASSES", "classes", required=True, singleton=False)
    assert spec.missing_message() == "missing CLASSES block"


def test_required_scalar_rejects_absent_and_empty() -> None:
    spec = NotationSectionSpec("LAYER", "scalar", required=True, singleton=True)
    assert spec.rejects(None)
    assert spec.rejects("")
    assert not spec.rejects("Domain")


def test_required_classes_block_accepts_empty_body() -> None:
    spec = NotationSectionSpec("CLASSES", "classes", required=True, singleton=False)
    assert spec.rejects(None)
    assert not spec.rejects("")


def test_optional_section_never_rejects() -> None:
    spec = NotationSectionSpec("EXPORTS", "name_list", required=False, singleton=False)
    assert not spec.rejects(None)
    assert not spec.rejects("")
