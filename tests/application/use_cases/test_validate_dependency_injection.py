"""Tests for validate_dependency_injection orchestrator detection."""

from squeaky_clean.application.use_cases.validate_dependency_injection import (
    validate_dependency_injection,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, pattern: str, methods: tuple[str, ...],
         fields: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(name=name, pattern=pattern, implements=None,
                     methods=methods, depends=(), concretes=(), fields=fields)


def _arch(*classes: ClassSpec) -> ArchitectureSpec:
    mod = ModuleSpec(name="M", layer=LayerType.APPLICATION, exports=(),
                     depends=(), classes=classes, invariants=())
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def test_usecase_with_empty_fields_and_a_port_is_flagged() -> None:
    arch = _arch(
        _cls("XPort", "Gateway", ("publish(e: E): None",), ()),
        _cls("DoThing", "UseCase", ("run(x: int): int",), ()),
    )
    violations = validate_dependency_injection(arch)
    assert len(violations) == 1
    assert "DoThing" in violations[0] and "XPort" in violations[0]


def test_usecase_that_declares_its_port_is_ok() -> None:
    arch = _arch(
        _cls("XPort", "Gateway", ("publish(e: E): None",), ()),
        _cls("DoThing", "UseCase", ("run(x: int): int",), ("xPort: XPort",)),
    )
    assert validate_dependency_injection(arch) == ()


def test_no_port_in_module_is_not_flagged() -> None:
    # a UseCase with no Gateway/Repository around may be genuinely stateless
    arch = _arch(_cls("DoThing", "UseCase", ("run(x: int): int",), ()))
    assert validate_dependency_injection(arch) == ()


def test_value_object_is_never_flagged() -> None:
    arch = _arch(
        _cls("XPort", "Gateway", ("publish(e: E): None",), ()),
        _cls("Money", "ValueObject", (), ()),
    )
    assert validate_dependency_injection(arch) == ()
