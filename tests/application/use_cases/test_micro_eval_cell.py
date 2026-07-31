"""Tests for the MicroEvalCell DTO (R5.4)."""

from squeaky_clean.application.evaluation.microeval.micro_eval_cell import (
    MicroEvalCell,
)


def test_defaults_and_fields() -> None:
    cell = MicroEvalCell(
        pattern="strategy", language="java", passed=False,
        compile_errors=2, classes_emitted=3, cost_usd=0.01,
    )
    assert cell.detail == ""
    assert (cell.pattern, cell.language) == ("strategy", "java")
    assert not cell.passed and cell.compile_errors == 2
