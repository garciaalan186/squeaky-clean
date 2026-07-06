"""Tests for JavaCompiler output parsing."""

from squeaky_clean.infrastructure.compilation.java_compiler import JavaCompiler

_OUTPUT = (
    "[ERROR] /p/src/main/java/com/example/EventController.java:[10,5] "
    "cannot find symbol\n"
    "[ERROR] /p/src/test/java/com/example/EventControllerTest.java:[63,32] "
    "cannot find symbol\n"
)


def test_parse_counts_all_compile_errors() -> None:
    result = JavaCompiler()._parse(_OUTPUT)
    assert result.ok is False
    assert result.error_count == 2


def test_parse_offending_stems_are_main_sources_only() -> None:
    result = JavaCompiler()._parse(_OUTPUT)
    # src/test errors are excluded (they signal test/impl drift, not a
    # production compile bug the compile gate should regenerate)
    assert result.offending_stems == ("EventController",)


def test_parse_clean_output_is_ok() -> None:
    result = JavaCompiler()._parse("BUILD SUCCESS")
    assert result.ok is True
    assert result.error_count == 0
