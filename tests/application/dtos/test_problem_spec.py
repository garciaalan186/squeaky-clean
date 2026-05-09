"""Tests for ProblemSpec."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def test_problem_spec_stores_all_fields() -> None:
    spec = ProblemSpec(
        id="P0",
        tier=0,
        slug="calculator",
        description="calc",
        required_bounded_contexts=["c"],
        acceptance_criteria=["a"],
        expected_module_count=(1, 1),
        expected_class_count=(3, 6),
        required_patterns=["SimpleClass"],
        target_language=TargetLanguage.PYTHON,
    )
    assert spec.id == "P0"
    assert spec.tier == 0
    assert spec.slug == "calculator"
    assert spec.expected_module_count == (1, 1)
    assert spec.required_patterns == ["SimpleClass"]
    assert spec.target_language is TargetLanguage.PYTHON
