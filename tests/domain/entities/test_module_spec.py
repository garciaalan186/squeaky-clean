"""Tests for ModuleSpec."""

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def _cls(
    name: str,
    pattern: PatternName = "SimpleClass",
    methods: tuple[str, ...] = (),
    depends: tuple[str, ...] = (),
    fields: tuple[str, ...] = (),
) -> ClassSpec:
    return ClassSpec(
        name=name, pattern=pattern, implements=None,
        methods=methods, depends=depends, concretes=(), fields=fields,
    )


def _module(cls: ClassSpec) -> ModuleSpec:
    return ModuleSpec(
        name="M", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )


def test_module_spec_construction() -> None:
    spec = _module(_cls("Calculator"))
    assert spec.name == "M"
    assert spec.layer is LayerType.DOMAIN
    assert spec.classes[0].name == "Calculator"


def test_module_spec_validate_empty_module() -> None:
    assert _module(_cls("Calculator")).validate() == []


def test_module_spec_validate_unknown_dependency() -> None:
    spec = _module(_cls("A", depends=("Ghost",)))
    assert any("Ghost" in v for v in spec.validate())


def test_module_spec_validate_accepts_well_formed_fields() -> None:
    cls = _cls(
        "Todo", pattern="Entity",
        methods=("mark_complete(): None", "is_pending(): bool"),
        fields=("id: TodoId", "title: TodoTitle"),
    )
    assert _module(cls).validate() == []


def test_module_spec_validate_rejects_malformed_fields() -> None:
    cls = _cls("Broken", pattern="Entity", fields=("no_colon_here",))
    assert any("field" in v for v in _module(cls).validate())


def test_module_spec_validate_accepts_four_methods() -> None:
    """Method count is a soft metric, not a hard gate (Clean Code SRP)."""
    cls = _cls(
        "Calculator",
        methods=("a(): int", "b(): int", "c(): int", "d(): int"),
    )
    assert _module(cls).validate() == []
