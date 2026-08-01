"""Tests for ClassFieldExtractor: annotated + self-assigned field recovery."""

import ast

from squeaky_clean.application.generation.recovery.extraction.class_field_extractor import (
    ClassFieldExtractor,
)


def _class_node(source: str) -> ast.ClassDef:
    node = ast.parse(source).body[0]
    assert isinstance(node, ast.ClassDef)
    return node


def test_annotated_class_attributes_keep_their_rendered_type() -> None:
    node = _class_node("class C:\n    x: int\n    y: list[str]\n")
    assert ClassFieldExtractor().extract(node) == ("x: int", "y: list[str]")


def test_self_assignments_are_emitted_bare() -> None:
    node = _class_node(
        "class C:\n    def __init__(self):\n        self.total = 0\n",
    )
    assert ClassFieldExtractor().extract(node) == ("total",)


def test_annotation_wins_over_duplicate_self_assignment() -> None:
    node = _class_node(
        "class C:\n    x: int\n"
        "    def __init__(self):\n        self.x = 0\n        self.y = 1\n",
    )
    assert ClassFieldExtractor().extract(node) == ("x: int", "y")


def test_non_self_attribute_stores_are_ignored() -> None:
    node = _class_node(
        "class C:\n    def m(self, other):\n        other.x = 1\n",
    )
    assert ClassFieldExtractor().extract(node) == ()
