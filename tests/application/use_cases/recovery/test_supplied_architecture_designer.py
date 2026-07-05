"""Tests for SuppliedArchitectureDesigner (Stage-6 architect short-circuit)."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.recovery.supplied_architecture_designer import (
    SuppliedArchitectureDesigner,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_SPEC = ArchitectureSpec(
    modules=(
        ModuleSpec(
            name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
            classes=(ClassSpec(
                name="Order", pattern="Entity", implements=None,
                methods=("total(): int",), depends=(), concretes=(), fields=("id: str",),
            ),),
            invariants=(),
        ),
    ),
    graph=ArchitectureGraph(edges={"Shop": ()}),
)

_PROBLEM = ProblemSpec(
    id="RECOVERED", tier=0, slug="recovered", description="x",
    required_bounded_contexts=[], acceptance_criteria=[],
    expected_module_count=(1, 1), expected_class_count=(1, 1),
    required_patterns=[], target_language=TargetLanguage.PYTHON,
)


def test_is_a_design_architecture() -> None:
    assert isinstance(SuppliedArchitectureDesigner(_SPEC, "sq"), DesignArchitecture)


def test_execute_returns_the_supplied_spec() -> None:
    designer = SuppliedArchitectureDesigner(_SPEC, "sq")
    assert designer.execute(_PROBLEM) is _SPEC


def test_last_raw_notation_is_the_supplied_squib() -> None:
    designer = SuppliedArchitectureDesigner(_SPEC, "MODULE Shop\n...")
    designer.execute(_PROBLEM)
    assert designer.last_raw_notation == "MODULE Shop\n..."
