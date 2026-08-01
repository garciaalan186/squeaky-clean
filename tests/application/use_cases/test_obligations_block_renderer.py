"""Tests for ObligationsBlockRenderer (extracted from the context formatter)."""

from squeaky_clean.application.generation.testgen.prompting.obligations_block_renderer import (
    ObligationsBlockRenderer,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _problem(criteria: list[str]) -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=1, slug="x", description="d",
        required_bounded_contexts=["m"],
        acceptance_criteria=criteria,
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["Entity"],
        target_language=TargetLanguage.PYTHON,
    )


def _module(layer: LayerType, classes: tuple[ClassSpec, ...]) -> ModuleSpec:
    return ModuleSpec(
        name="Archival", layer=layer,
        exports=tuple(c.name for c in classes), depends=(),
        classes=classes, invariants=(),
    )


def test_infrastructure_module_gets_integration_only_block() -> None:
    module = _module(LayerType.INFRASTRUCTURE, ())
    ctx = TestArchitectureContext(module=module, problem=_problem([]))
    lines = ObligationsBlockRenderer().render(ctx)
    assert len(lines) == 1
    assert "Emit ZERO tests here" in lines[0]


def test_no_architecture_means_no_obligations_block() -> None:
    module = _module(LayerType.APPLICATION, ())
    ctx = TestArchitectureContext(module=module, problem=_problem([]))
    assert ObligationsBlockRenderer().render(ctx) == []


def test_behavioural_obligation_for_owned_class_is_rendered() -> None:
    use_case = ClassSpec(
        name="ArchiveEventUseCase", pattern="UseCase", implements=None,
        methods=("archive_event(e: Event): Result",),
        depends=(), concretes=(),
    )
    module = _module(LayerType.APPLICATION, (use_case,))
    problem = _problem(
        ["Given X, When archive_event is called, Then result is ok"],
    )
    ctx = TestArchitectureContext(
        module=module, problem=problem,
        architecture=ArchitectureSpec.single(module),
    )
    lines = ObligationsBlockRenderer().render(ctx)
    assert lines[0].startswith("TestObligations")
    assert any("ArchiveEventUseCase.archive_event" in line for line in lines[1:])
