"""Tests for JavacCompiler (R5.4). Output parsing only — no JDK required."""

from pathlib import Path

from squeaky_clean.infrastructure.compilation.javac_compiler import JavacCompiler

_JAVAC_OUTPUT = (
    "src/FixedAmountDiscount.java:4: error: interface expected here\n"
    "public class FixedAmountDiscount implements DiscountStrategy {\n"
    "src/Cart.java:54: error: incompatible types\n"
    "2 errors\n"
)


def test_parse_counts_errors_and_stems() -> None:
    result = JavacCompiler._parse(_JAVAC_OUTPUT)
    assert not result.ok
    assert result.error_count == 2
    assert result.offending_stems == ("Cart", "FixedAmountDiscount")


def test_parse_clean_output_is_ok() -> None:
    result = JavacCompiler._parse("")
    assert result.ok and result.error_count == 0


def test_empty_project_dir_fails_loudly(tmp_path: Path) -> None:
    result = JavacCompiler().compile(tmp_path)
    assert not result.ok
    assert "no .java files" in result.raw_output
