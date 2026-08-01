"""Tests for ClassGrammar: the per-language regex triple."""

import re

from squeaky_clean.application.generation.recovery.extraction.class_grammar import ClassGrammar

_CLASS = re.compile(r"class\s+(?P<name>\w+)")
_METHOD = re.compile(r"(?P<name>\w+)\((?P<args>[^)]*)\)")
_FIELD = re.compile(r"(?P<name>\w+):\s*(?P<type>\w+)")


def test_carries_the_three_declaration_regexes() -> None:
    grammar = ClassGrammar(class_re=_CLASS, method_re=_METHOD, field_re=_FIELD)
    assert grammar.class_re.search("class Order").group("name") == "Order"
    assert grammar.method_re.search("total()").group("name") == "total"
    assert grammar.field_re.search("id: str").group("type") == "str"


def test_is_a_frozen_value_object() -> None:
    grammar = ClassGrammar(class_re=_CLASS, method_re=_METHOD, field_re=_FIELD)
    assert grammar == ClassGrammar(class_re=_CLASS, method_re=_METHOD, field_re=_FIELD)
    try:
        grammar.class_re = _METHOD  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised
