"""Tests for filter_criteria_for_module."""

from squeaky_clean.application.use_cases.per_module_criterion_filter import (
    filter_criteria_for_module,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def _cls(
    name: str, methods: tuple[str, ...] = (),
    pattern: PatternName = "Entity",
) -> ClassSpec:
    return ClassSpec(
        name=name, pattern=pattern, implements=None,
        methods=methods, depends=(), concretes=(),
    )


def _module(
    name: str, classes: tuple[ClassSpec, ...],
    layer: LayerType = LayerType.APPLICATION,
) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=layer,
        exports=tuple(c.name for c in classes), depends=(),
        classes=classes, invariants=(),
    )


def test_calculator_all_verbs_owned_keeps_all_three() -> None:
    criteria = (
        "Given operands 2 and 3, When add is called, Then result is 5",
        "Given operands 5 and 2, When subtract is called, Then result is 3",
        "Given operands 4 and 3, When multiply is called, Then result is 12",
    )
    calc = _cls("Calculator", methods=(
        "add(a: int, b: int): int",
        "subtract(a: int, b: int): int",
        "multiply(a: int, b: int): int",
    ), pattern="SimpleClass")
    module = _module("Calc", (calc,), layer=LayerType.DOMAIN)
    assert filter_criteria_for_module(criteria, module) == criteria


def test_persister_domain_module_with_no_owned_verbs_returns_empty() -> None:
    # Twitter/persister-style: 13 criteria, persister Domain owns no verbs
    criteria = tuple(
        f"Given X, When verb_{i} is called, Then result is Y"
        for i in range(13)
    )
    # Domain module with only entities (no methods relevant)
    archival = _module(
        "Archival", (_cls("ConsumedEvent"),),
        layer=LayerType.DOMAIN,
    )
    assert filter_criteria_for_module(criteria, archival) == ()


def test_criterion_without_when_clause_is_kept() -> None:
    criteria = (
        "Given an empty repository, the system is idle",
        "Given operands 1 and 2, When add is called, Then result is 3",
    )
    module = _module("M", (_cls(
        "C", methods=("add(a: int, b: int): int",), pattern="SimpleClass",
    ),))
    out = filter_criteria_for_module(criteria, module)
    assert out == criteria


def test_module_with_no_methods_returns_empty() -> None:
    criteria = (
        "Given X, When add is called, Then result is Y",
    )
    module = _module("M", (_cls("Empty", methods=()),))
    assert filter_criteria_for_module(criteria, module) == ()


def test_verb_match_is_case_insensitive() -> None:
    criteria = (
        "Given X, When IngestEvent is called, Then result is Y",
    )
    module = _module("M", (_cls(
        "C", methods=("ingest_event(e: Event): IngestedEvent",),
        pattern="UseCase",
    ),))
    assert filter_criteria_for_module(criteria, module) == criteria


def test_verb_match_is_underscore_insensitive() -> None:
    criteria = (
        "Given X, When ingest_event is called, Then result is Y",
    )
    module = _module("M", (_cls(
        "C", methods=("ingestEvent(e: Event): IngestedEvent",),
        pattern="UseCase",
    ),))
    assert filter_criteria_for_module(criteria, module) == criteria


def test_first_identifier_after_when_is_taken() -> None:
    # "When consume_event is called, Then ... When archive_event is also..."
    criteria = (
        "Given X, When consume_event is called and archive_event also runs, Then Y",
    )
    consume_only = _module("M", (_cls(
        "C", methods=("consume_event(m: Msg): Event",), pattern="UseCase",
    ),))
    archive_only = _module("N", (_cls(
        "D", methods=("archive_event(e: Event): None",), pattern="UseCase",
    ),))
    assert filter_criteria_for_module(criteria, consume_only) == criteria
    # First identifier after "When" is consume_event, NOT archive_event
    assert filter_criteria_for_module(criteria, archive_only) == ()


def test_module_with_zero_classes_returns_empty() -> None:
    criteria = ("Given X, When add is called, Then Y",)
    module = ModuleSpec(
        name="Empty", layer=LayerType.DOMAIN,
        exports=(), depends=(), classes=(), invariants=(),
    )
    assert filter_criteria_for_module(criteria, module) == ()


def test_domain_layer_with_only_value_objects_returns_empty() -> None:
    criteria = (
        "Given X, When operate is called, Then result is Y",
    )
    vo = _cls("Money", methods=("operate(): int",), pattern="ValueObject")
    module = _module("Shared", (vo,), layer=LayerType.DOMAIN)
    assert filter_criteria_for_module(criteria, module) == ()


def test_application_layer_with_use_case_keeps_match() -> None:
    criteria = (
        "Given X, When archive_event is called, Then Y",
    )
    use_case = _cls(
        "ArchiveEventUseCase",
        methods=("archive_event(e: Event): None",),
        pattern="UseCase",
    )
    module = _module(
        "Archival", (use_case,), layer=LayerType.APPLICATION,
    )
    assert filter_criteria_for_module(criteria, module) == criteria


def test_unmatched_verb_dropped_when_module_has_other_methods() -> None:
    criteria = (
        "Given X, When delete is called, Then Y",
        "Given X, When add is called, Then Y",
    )
    module = _module("M", (_cls(
        "C", methods=("add(a: int): int",), pattern="SimpleClass",
    ),))
    out = filter_criteria_for_module(criteria, module)
    assert out == ("Given X, When add is called, Then Y",)
