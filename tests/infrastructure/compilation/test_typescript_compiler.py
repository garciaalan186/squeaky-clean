"""Tests for TypeScriptCompiler output parsing."""

from squeaky_clean.infrastructure.compilation.typescript_compiler import (
    TypeScriptCompiler,
)

_OUTPUT = (
    "src/kafkaProducerPort.ts(3,29): error TS2304: Cannot find name 'X'.\n"
    "src/ingestEventUseCase.ts(20,11): error TS2741: Property missing.\n"
    "tests/ingestEventUseCase.test.ts(6,19): error TS2554: bad arity.\n"
)


def test_parse_counts_all_errors_including_test_files() -> None:
    result = TypeScriptCompiler()._parse(_OUTPUT)
    assert result.ok is False
    assert result.error_count == 3


def test_parse_offending_stems_are_src_only() -> None:
    result = TypeScriptCompiler()._parse(_OUTPUT)
    # test-file errors are excluded from the fixer-driving stems
    assert result.offending_stems == ("kafkaProducerPort", "ingestEventUseCase")


def test_parse_clean_output_is_ok() -> None:
    result = TypeScriptCompiler()._parse("")
    assert result.ok is True
    assert result.error_count == 0
    assert result.offending_stems == ()
