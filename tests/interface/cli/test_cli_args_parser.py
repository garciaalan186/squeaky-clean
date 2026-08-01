"""Tests for CLIArgsParser (input-mode validation + problem-id resolution).

Per-flag-block coverage lives in tests/interface/cli/flags/ mirroring the
registrar modules; this file keeps the parser-level contract tests.
"""

import pytest

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver


def test_no_problem_arg_errors_out() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse([])


def test_no_input_mode_is_rejected() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse([])


def test_problem_and_problems_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse(["--problem", "P0", "--problems", "P0,P1"])


def test_p0go_id_resolves_to_go_problem_spec() -> None:
    args = CLIArgsParser().parse(["--problem", "P0GO"])
    assert args.problem_ids == ("P0GO",)
    spec = ProblemResolver().resolve("P0GO")
    assert spec.id == "P0GO"
    assert spec.target_language is TargetLanguage.GO
    assert spec.slug == "calculator"


def test_p0rust_id_resolves_to_rust_problem_spec() -> None:
    args = CLIArgsParser().parse(["--problem", "P0RUST"])
    assert args.problem_ids == ("P0RUST",)
    spec = ProblemResolver().resolve("P0RUST")
    assert spec.id == "P0RUST"
    assert spec.target_language is TargetLanguage.RUST
    assert spec.slug == "calculator"
