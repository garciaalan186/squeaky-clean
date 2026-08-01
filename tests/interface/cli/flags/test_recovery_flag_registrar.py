"""Tests for RecoveryFlagRegistrar (recovery/triage/refactor flag family)."""

import pytest

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


def test_squib_file_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--squib-file", "out/recovered.squib"])
    assert args.squib_file == "out/recovered.squib"
    assert args.problem_ids == ()


def test_legacy_tests_flag_is_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--squib-file", "r.squib", "--legacy-tests", "legacy/tests"],
    )
    assert args.legacy_tests == "legacy/tests"


def test_recover_from_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--recover-from", "some/project"])
    assert args.recover_from == "some/project"
    assert args.problem_ids == ()


def test_recover_language_defaults_to_python() -> None:
    assert CLIArgsParser().parse(["--recover-from", "p"]).recover_language == "python"


def test_recover_language_flag_is_parsed() -> None:
    args = CLIArgsParser().parse(["--recover-from", "p", "--language", "java"])
    assert args.recover_language == "java"


def test_unknown_language_is_rejected() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse(["--recover-from", "p", "--language", "cobol"])


def test_criteria_are_parsed_in_order() -> None:
    args = CLIArgsParser().parse(
        ["--recover-from", "p", "--criteria", "testability, simplicity ,performance"],
    )
    assert args.criteria == ("testability", "simplicity", "performance")


def test_recover_out_flag_is_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--recover-from", "p", "--recover-out", "out/x.squib"],
    )
    assert args.recover_out == "out/x.squib"


def test_triage_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--triage", "out/violations.json"])
    assert args.triage == "out/violations.json"
    assert args.problem_ids == ()


def test_refactor_and_plan_flags_are_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--refactor", "recovered.squib", "--plan", "refactor_plan.json"],
    )
    assert args.refactor == "recovered.squib"
    assert args.plan == "refactor_plan.json"


def test_refactor_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--refactor", "recovered.squib"])
    assert args.refactor == "recovered.squib"
    assert args.problem_ids == ()
