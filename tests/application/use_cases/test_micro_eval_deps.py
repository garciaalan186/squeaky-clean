"""Tests for the MicroEvalDeps bundle (R5.4)."""

from pathlib import Path

from squeaky_clean.application.evaluation.microeval.micro_eval_deps import (
    MicroEvalDeps,
)


def test_extra_files_default_empty() -> None:
    deps = MicroEvalDeps(
        implementers={}, compilers={}, out_root=Path("/tmp/x"),
    )
    assert deps.extra_files == {}
    assert deps.implementers == {} and deps.compilers == {}
