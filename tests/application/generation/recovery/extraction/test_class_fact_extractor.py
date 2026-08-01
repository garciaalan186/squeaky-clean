"""Tests for ClassFactExtractor: one ClassRecord from one ast.ClassDef."""

import ast

from squeaky_clean.application.generation.recovery.extraction.class_fact_extractor import (
    ClassFactExtractor,
)


def _class_node(source: str) -> ast.ClassDef:
    node = ast.parse(source).body[0]
    assert isinstance(node, ast.ClassDef)
    return node


def test_public_methods_drop_self_and_render_arg_names() -> None:
    node = _class_node(
        "class C:\n"
        "    def pay(self, amount, currency): ...\n"
        "    def _helper(self): ...\n",
    )
    record = ClassFactExtractor().record(node, "p.C", ())
    assert record.methods == ("pay(amount, currency)",)


def test_bases_and_fqn_and_imports_carry_through() -> None:
    node = _class_node("class C(Base, abc.ABC): ...\n")
    record = ClassFactExtractor().record(node, "p.C", ("p.base.Base",))
    assert record.fqn == "p.C"
    assert record.bases == ("Base", "abc.ABC")
    assert record.imports == ("p.base.Base",)


def test_decorators_include_method_level_route_signals() -> None:
    node = _class_node(
        "class C:\n"
        "    @app.route('/x')\n"
        "    def index(self): ...\n",
    )
    record = ClassFactExtractor().record(node, "p.C", ())
    assert record.decorators == ("app.route('/x')",)


def test_class_level_decorators_come_before_method_level() -> None:
    node = _class_node(
        "@dataclass\n"
        "class C:\n"
        "    @cached\n"
        "    def m(self): ...\n",
    )
    record = ClassFactExtractor().record(node, "p.C", ())
    assert record.decorators == ("dataclass", "cached")
