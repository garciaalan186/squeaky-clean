"""Tests for ClassPaths block emission in TestArchitectureContextFormatter."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.test_architecture_context_formatter import (
    TestArchitectureContextFormatter,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _cls(name: str, pattern: PatternName = "Entity") -> ClassSpec:
    return ClassSpec(
        name=name, pattern=pattern, implements=None,
        methods=(), depends=(), concretes=(),
    )


def _module(
    name: str, layer: LayerType, classes: tuple[ClassSpec, ...],
) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=layer,
        exports=tuple(c.name for c in classes), depends=(),
        classes=classes, invariants=(),
    )


def _ctx(arch: ArchitectureSpec | None, focal: ModuleSpec) -> TestArchitectureContext:
    return TestArchitectureContext(
        module=focal, problem=P0,
        toolkit=LanguageToolkitFactory().for_language(TargetLanguage.PYTHON),
        architecture=arch,
    )


def test_class_paths_block_lists_every_architecture_class() -> None:
    archival = _module(
        "Archival", LayerType.DOMAIN, (_cls("ConsumedEvent"),),
    )
    consumption = _module(
        "ConsumptionInfrastructure", LayerType.INFRASTRUCTURE,
        (_cls("KafkaConsumerAdapter", "Adapter"),),
    )
    use_case = _module(
        "Archival", LayerType.APPLICATION,
        (_cls("ArchiveEventUseCase", "UseCase"),),
    )
    arch = ArchitectureSpec(
        modules=(archival, consumption, use_case),
        graph=ArchitectureGraph(edges={}),
    )
    ctx = _ctx(arch, archival)
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "ClassPaths:" in rendered
    assert "  - ConsumedEvent: src.domain.archival.consumed_event" in rendered
    assert (
        "  - KafkaConsumerAdapter: "
        "src.infrastructure.consumption_infrastructure.kafka_consumer_adapter"
    ) in rendered
    assert (
        "  - ArchiveEventUseCase: "
        "src.application.archival.archive_event_use_case"
    ) in rendered


def test_class_paths_omitted_when_architecture_has_no_classes() -> None:
    empty_module = ModuleSpec(
        name="Empty", layer=LayerType.DOMAIN,
        exports=(), depends=(), classes=(), invariants=(),
    )
    # Force-bypass ModuleSpec.validate by going through ArchitectureSpec
    # construction directly (validate is not invoked at __init__ time).
    arch = ArchitectureSpec(
        modules=(empty_module,), graph=ArchitectureGraph(edges={}),
    )
    ctx = _ctx(arch, empty_module)
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "ClassPaths:" not in rendered


def test_class_paths_uses_focal_module_when_no_architecture() -> None:
    focal = _module("Calc", LayerType.DOMAIN, (_cls("Calculator", "SimpleClass"),))
    ctx = _ctx(None, focal)
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "ClassPaths:" in rendered
    assert "  - Calculator: src.domain.calc.calculator" in rendered


def test_class_paths_per_language_emission_for_java() -> None:
    focal = _module("Calc", LayerType.DOMAIN, (_cls("Calculator", "SimpleClass"),))
    ctx = TestArchitectureContext(
        module=focal, problem=P0,
        toolkit=LanguageToolkitFactory().for_language(TargetLanguage.JAVA),
    )
    rendered = TestArchitectureContextFormatter().format(ctx)
    assert "ClassPaths:" in rendered
    assert "  - Calculator: com.example.Calculator" in rendered
