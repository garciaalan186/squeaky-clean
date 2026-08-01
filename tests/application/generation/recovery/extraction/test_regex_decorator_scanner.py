"""Tests for RegexDecoratorScanner: class- and method-level annotation capture."""

from squeaky_clean.application.generation.recovery.extraction.regex_decorator_scanner import (
    RegexDecoratorScanner,
)


def test_contiguous_leading_annotations_are_collected_nearest_first() -> None:
    source = "@RestController\n@RequestMapping\nclass A {"
    names = RegexDecoratorScanner().scan(source, source.index("class"), "")
    assert names == ("RequestMapping", "RestController")


def test_blank_line_breaks_the_leading_annotation_run() -> None:
    source = "@Far\n\n@Near\nclass A {"
    names = RegexDecoratorScanner().scan(source, source.index("class"), "")
    assert names == ("Near",)


def test_non_annotation_line_stops_the_upward_walk() -> None:
    source = "import x\n@Only\nclass A {"
    names = RegexDecoratorScanner().scan(source, source.index("class"), "")
    assert names == ("Only",)


def test_body_annotations_are_appended_and_deduplicated() -> None:
    source = "@Controller\nclass A {"
    body = "  @GetMapping\n  run() {}\n  @Controller\n"
    names = RegexDecoratorScanner().scan(source, source.index("class"), body)
    assert names == ("Controller", "GetMapping")
