"""Tests for the Refactor phase: FrameworkCouplingTransform + RefactorPhase."""

from squeaky_clean.application.dtos.recovery.refactor_plan import RefactorPlan
from squeaky_clean.application.use_cases.recovery.framework_coupling_transform import (
    FrameworkCouplingTransform,
)
from squeaky_clean.application.use_cases.recovery.refactor_phase import RefactorPhase
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, method: str) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="SimpleClass", implements=None, methods=(method,),
        depends=(), concretes=(), fields=(), invariants=(),
    )


_SHOP = ModuleSpec(
    name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
    classes=(_cls("Order", "total(): int"), _cls("Page", "render(): str")),
    invariants=(),
)
_SPEC = ArchitectureSpec(modules=(_SHOP,), graph=ArchitectureGraph(edges={"Shop": ()}))


def _split() -> ArchitectureSpec:
    return FrameworkCouplingTransform().apply(_SPEC, frozenset({"Page"}))


def _module(spec: ArchitectureSpec, name: str) -> ModuleSpec:
    return next(m for m in spec.modules if m.name == name)


def test_target_becomes_entity_plus_repository_in_place() -> None:
    patterns = {c.name: c.pattern for c in _module(_split(), "Shop").classes}
    assert patterns["Page"] == "Entity"
    assert patterns["PageRepository"] == "Repository"
    assert patterns["Order"] == "SimpleClass"  # untouched


def test_adapter_moves_to_a_companion_infra_module() -> None:
    infra = _module(_split(), "ShopInfra")
    assert infra.layer is LayerType.INFRASTRUCTURE
    assert infra.classes[0].name == "PageAdapter"
    assert infra.classes[0].pattern == "Adapter"


def test_entity_and_repository_are_exported() -> None:
    assert set(_module(_split(), "Shop").exports) == {"Page", "PageRepository"}


def test_infra_depends_inward_and_result_validates() -> None:
    spec = _split()
    assert spec.graph.edges["ShopInfra"] == ("Shop",)
    assert spec.validate() == ()


def test_phase_applies_only_fix_selected_coupling() -> None:
    plan = RefactorPlan(fix=("framework-coupling:shop.page.Page",), ignore=())
    names = {c.name for m in RefactorPhase().apply(_SPEC, plan).modules for c in m.classes}
    assert {"Page", "PageRepository", "PageAdapter"} <= names


def test_phase_is_a_noop_without_coupling_fixes() -> None:
    plan = RefactorPlan(fix=("granularity:God",), ignore=())
    assert RefactorPhase().apply(_SPEC, plan) is _SPEC
