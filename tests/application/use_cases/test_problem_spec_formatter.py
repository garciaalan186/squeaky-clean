"""Tests for ProblemSpecFormatter — including new domain-semantics sections."""

import pytest

from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.entity_lifecycle import EntityLifecycle, StateTransition
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.query_semantic import QuerySemantic
from squeaky_clean.application.use_cases.problem_spec_formatter import ProblemSpecFormatter
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _spec(**kw: object) -> ProblemSpec:
    base: dict[str, object] = dict(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=["x"], acceptance_criteria=["a"],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["SimpleClass"], target_language=TargetLanguage.PYTHON,
    )
    base.update(kw)
    return ProblemSpec(**base)  # type: ignore[arg-type]


def test_renders_domain_conventions_with_expanded_text() -> None:
    spec = _spec(domain_conventions=("timeline_includes_self",))
    out = ProblemSpecFormatter().format(spec)
    assert "DomainConventions:" in out
    assert "timeline_includes_self" in out
    assert "user's own posts" in out


def test_renders_query_semantics_lifecycle_classification() -> None:
    spec = _spec(
        query_semantics=(QuerySemantic(use_case="GetTimelineUseCase",
                                       shape="self_plus_followees"),),
        entity_lifecycle=(EntityLifecycle(entity="Tweet", transitions=(
            StateTransition(from_state="draft", to_state="published",
                            trigger="publish"),)),),
        data_classification=(DataClassification(
            field_ref="User.password_hash", sensitivity="credential"),),
    )
    out = ProblemSpecFormatter().format(spec)
    assert "QuerySemantics:" in out
    assert "GetTimelineUseCase: self_plus_followees" in out
    assert "EntityLifecycle:" in out
    assert "Tweet: draft → published (publish)" in out
    assert "DataClassification:" in out
    assert "User.password_hash: credential" in out


def test_unknown_convention_raises() -> None:
    spec = _spec(domain_conventions=("not_a_real_tag",))
    with pytest.raises(ValueError):
        ProblemSpecFormatter().format(spec)


def test_omits_sections_when_empty() -> None:
    spec = _spec()
    out = ProblemSpecFormatter().format(spec)
    assert "DomainConventions:" not in out
    assert "QuerySemantics:" not in out
