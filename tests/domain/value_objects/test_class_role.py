"""Tests for ClassRole enum."""

from squeaky_clean.domain.value_objects.class_role import ClassRole


def test_class_role_has_exactly_three_members() -> None:
    assert {r.name for r in ClassRole} == {"ABSTRACT", "CONCRETE", "PLAIN"}


def test_class_role_values() -> None:
    assert ClassRole.ABSTRACT.value == "abstract"
    assert ClassRole.CONCRETE.value == "concrete"
    assert ClassRole.PLAIN.value == "plain"


def test_class_role_members_are_distinct() -> None:
    assert len({r.value for r in ClassRole}) == 3
