"""Tests for select_infrastructure_choices (H3)."""

import pytest

from squeaky_clean.application.dtos.derived_infrastructure_choice import (
    DerivedInfrastructureChoice,
)
from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.select_infrastructure_choices import (
    MissingInfrastructureChoiceError,
    select_infrastructure_choices,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class _StubArchitect:
    def __init__(self, choice: DerivedInfrastructureChoice) -> None:
        self._choice = choice
        self.call_count = 0

    def decide(self, problem: ProblemSpec, category: str) -> DerivedInfrastructureChoice:
        self.call_count += 1
        return self._choice


def _problem(*, choices: tuple[InfrastructureChoice, ...] = ()) -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
        infrastructure_choices=choices,
    )


def test_explicit_choices_pass_through_when_inference_off() -> None:
    explicit = InfrastructureChoice(
        category="blob_storage", technology="s3", version_pin="boto3==1.34",
    )
    out = select_infrastructure_choices(
        _problem(choices=(explicit,)), frozenset({"blob_storage"}),
        infer_enabled=False, choice_architect=None,
    )
    assert out == (explicit,)


def test_missing_required_raises_when_inference_off() -> None:
    with pytest.raises(MissingInfrastructureChoiceError, match="kv_cache"):
        select_infrastructure_choices(
            _problem(), frozenset({"kv_cache"}),
            infer_enabled=False, choice_architect=None,
        )


def test_inference_on_invokes_architect_for_missing_category() -> None:
    derived = DerivedInfrastructureChoice(
        category="kv_cache", technology="redis", version_pin="redis-py==5.0",
        scores={"ops": 4}, weighted_score=4.0, rationale="r",
    )
    stub = _StubArchitect(derived)
    out = select_infrastructure_choices(
        _problem(), frozenset({"kv_cache"}),
        infer_enabled=True, choice_architect=stub,  # type: ignore[arg-type]
    )
    assert stub.call_count == 1
    assert out == (derived.to_choice(),)
