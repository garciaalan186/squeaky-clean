"""Tests for EmitterLangBlockFilter conditional-block resolution."""

from squeaky_clean.application.generation.emission.composition.emitter_lang_block_filter import (
    EmitterLangBlockFilter,
)

_TEMPLATE = """shared head
{{#lang:java}}
java only
{{/lang}}
{{#lang:python,typescript}}
py and ts
{{/lang}}
shared tail
"""


def test_keeps_matching_language_blocks() -> None:
    out = EmitterLangBlockFilter().filter(_TEMPLATE, "java")
    assert "java only" in out
    assert "py and ts" not in out


def test_comma_list_matches_each_language() -> None:
    for lang in ("python", "typescript"):
        out = EmitterLangBlockFilter().filter(_TEMPLATE, lang)
        assert "py and ts" in out
        assert "java only" not in out


def test_marker_lines_never_survive() -> None:
    out = EmitterLangBlockFilter().filter(_TEMPLATE, "java")
    assert "{{#lang:" not in out
    assert "{{/lang}}" not in out


def test_shared_lines_always_survive() -> None:
    out = EmitterLangBlockFilter().filter(_TEMPLATE, "go")
    assert "shared head" in out
    assert "shared tail" in out
