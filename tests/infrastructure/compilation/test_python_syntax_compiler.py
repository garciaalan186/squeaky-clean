"""Tests for PythonSyntaxCompiler (R5.4)."""

from pathlib import Path

from squeaky_clean.infrastructure.compilation.python_syntax_compiler import (
    PythonSyntaxCompiler,
)


def test_valid_python_passes(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("class Ok:\n    pass\n")
    result = PythonSyntaxCompiler().compile(tmp_path)
    assert result.ok and result.error_count == 0


def test_syntax_error_is_counted_with_stem(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("class Bad(:\n")
    (tmp_path / "ok.py").write_text("x = 1\n")
    result = PythonSyntaxCompiler().compile(tmp_path)
    assert not result.ok
    assert result.error_count == 1
    assert result.offending_stems == ("bad",)
    assert "bad.py" in result.raw_output
