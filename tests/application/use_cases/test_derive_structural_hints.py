"""Tests for derive_structural_hints_from_squib."""

from squeaky_clean.application.evaluation.eval.metrics.derive_structural_hints import (
    derive_structural_hints_from_squib,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, pattern: str) -> ClassSpec:
    return ClassSpec(name=name, pattern=pattern, implements=None,
                     methods=(), depends=(), concretes=())


def _module(name: str, classes: tuple[ClassSpec, ...]) -> ModuleSpec:
    return ModuleSpec(name=name, layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=classes, invariants=())


def test_hints_project_modules_and_classes() -> None:
    arch = ArchitectureSpec(
        modules=(
            _module("Billing", (_cls("Invoice", "Entity"),
                                _cls("Money", "ValueObject"))),
            _module("Catalog", (_cls("Item", "Entity"),)),
        ),
        graph=ArchitectureGraph(edges={}),
    )
    hints = derive_structural_hints_from_squib(arch)
    assert hints.required_bounded_contexts == ["Billing", "Catalog"]
    assert hints.expected_module_count == (2, 2)
    assert hints.expected_class_count == (3, 3)


def test_patterns_are_deduplicated_and_sorted() -> None:
    arch = ArchitectureSpec.single(
        _module("Billing", (_cls("Invoice", "Entity"),
                            _cls("Money", "ValueObject"),
                            _cls("Item", "Entity"))),
    )
    hints = derive_structural_hints_from_squib(arch)
    assert hints.required_patterns == ["Entity", "ValueObject"]


def test_empty_module_yields_zero_class_expectations() -> None:
    arch = ArchitectureSpec.single(_module("Empty", ()))
    hints = derive_structural_hints_from_squib(arch)
    assert hints.required_bounded_contexts == ["Empty"]
    assert hints.required_patterns == []
    assert hints.expected_class_count == (0, 0)
