"""Filter integration test for TestArchitectureContextFormatter."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.test_architecture_context_formatter import (
    TestArchitectureContextFormatter,
)
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


def test_formatter_omits_acceptance_criteria_when_module_has_no_relevant_verbs() -> None:
    consumed_event = ClassSpec(
        name="ConsumedEvent", pattern="Entity", implements=None,
        methods=(), depends=(), concretes=(),
    )
    archival = ModuleSpec(
        name="Archival", layer=LayerType.DOMAIN,
        exports=("ConsumedEvent",), depends=(),
        classes=(consumed_event,), invariants=(),
    )
    problem = _problem([
        "Given X, When consume_event is called, Then Y",
        "Given X, When archive_event is called, Then Y",
    ])
    ctx = TestArchitectureContext(
        module=archival, problem=problem,
        toolkit=LanguageToolkitFactory().for_language(TargetLanguage.PYTHON),
    )
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "AcceptanceCriteria:" not in rendered
    assert "consume_event" not in rendered
    assert "archive_event" not in rendered
    # Sanity: the rest of the prompt must still be present.
    assert "Module: Archival" in rendered
    assert "Classes:" in rendered


def test_formatter_keeps_acceptance_criteria_when_module_owns_verb() -> None:
    use_case = ClassSpec(
        name="ArchiveEventUseCase", pattern="UseCase", implements=None,
        methods=("archive_event(e: Event): None",),
        depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="Archival", layer=LayerType.APPLICATION,
        exports=("ArchiveEventUseCase",), depends=(),
        classes=(use_case,), invariants=(),
    )
    problem = _problem([
        "Given X, When archive_event is called, Then Y",
        "Given X, When unrelated_verb is called, Then Y",
    ])
    ctx = TestArchitectureContext(
        module=module, problem=problem,
        toolkit=LanguageToolkitFactory().for_language(TargetLanguage.PYTHON),
    )
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "AcceptanceCriteria:" in rendered
    assert "archive_event" in rendered
    assert "unrelated_verb" not in rendered
