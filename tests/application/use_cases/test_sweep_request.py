"""Tests for the SweepRequest DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _problem(pid: str) -> ProblemSpec:
    return ProblemSpec(
        id=pid, slug=pid.lower(), description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )


def test_max_parallel_defaults_to_four() -> None:
    request = SweepRequest(problems=(_problem("P0"),))
    assert request.max_parallel == 4


def test_stores_problems_and_explicit_cap() -> None:
    problems = (_problem("P0"), _problem("P1"))
    request = SweepRequest(problems=problems, max_parallel=2)
    assert request.problems == problems
    assert request.max_parallel == 2


def test_is_frozen() -> None:
    request = SweepRequest(problems=())
    with pytest.raises(dataclasses.FrozenInstanceError):
        request.max_parallel = 8  # type: ignore[misc]
