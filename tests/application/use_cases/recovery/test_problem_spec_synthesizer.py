"""Tests for ProblemSpecSynthesizer (Stage-6 thin ProblemSpec)."""

from pathlib import Path

from squeaky_clean.application.use_cases.recovery.problem_spec_synthesizer import (
    ProblemSpecSynthesizer,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _cls(name: str, pattern: str) -> ClassSpec:
    return ClassSpec(
        name=name, pattern=pattern, implements=None,  # type: ignore[arg-type]
        methods=(), depends=(), concretes=(), fields=(),
    )


_SPEC = ArchitectureSpec(
    modules=(
        ModuleSpec(
            name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
            classes=(_cls("Order", "Entity"), _cls("Money", "ValueObject")),
            invariants=(),
        ),
        ModuleSpec(
            name="Billing", layer=LayerType.DOMAIN, exports=(), depends=(),
            classes=(_cls("Invoice", "Entity"),), invariants=(),
        ),
    ),
    graph=ArchitectureGraph(edges={"Shop": (), "Billing": ()}),
)


def test_counts_and_contexts_track_the_spec() -> None:
    spec = ProblemSpecSynthesizer().synthesize(_SPEC)
    assert spec.expected_module_count == (2, 2)
    assert spec.expected_class_count == (3, 3)
    assert spec.required_bounded_contexts == ["Shop", "Billing"]
    assert spec.target_language is TargetLanguage.PYTHON


def test_required_patterns_are_the_distinct_recovered_patterns() -> None:
    spec = ProblemSpecSynthesizer().synthesize(_SPEC)
    assert spec.required_patterns == ["Entity", "ValueObject"]


def test_no_tests_dir_yields_no_criteria() -> None:
    assert ProblemSpecSynthesizer().synthesize(_SPEC).acceptance_criteria == []


def test_criteria_derived_from_legacy_test_functions(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_order.py").write_text(
        "def test_total_sums_line_items():\n    pass\n\n"
        "def helper():\n    pass\n\n"
        "def test_rejects_empty_order():\n    pass\n"
    )
    criteria = ProblemSpecSynthesizer().synthesize(_SPEC, tests).acceptance_criteria
    assert criteria == ["total sums line items", "rejects empty order"]
