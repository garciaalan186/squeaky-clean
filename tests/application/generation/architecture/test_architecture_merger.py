"""Tests for ArchitectureMerger: N module outputs collapsed to one flat bundle."""

from squeaky_clean.application.generation.architecture.architecture_merger import (
    ArchitectureMerger,
)
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import (
    ModuleImplementation,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_skeleton import TestSkeleton
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(name: str, layer: LayerType, cls: str) -> ModuleSpec:
    spec = ClassSpec(name=cls, pattern="SimpleClass", implements=None,
                     methods=(), depends=(), concretes=())
    return ModuleSpec(name=name, layer=layer, exports=(cls,),
                      depends=(), classes=(spec,), invariants=(f"{name} rule",))


def _impl(module: ModuleSpec, cost: float, wall: int) -> ModuleImplementation:
    ic = ImplementedClass(class_name=module.classes[0].name, file_path="src/x.py",
                          code="pass", test_code=None, cost_usd=cost,
                          duration_ms=10, input_tokens=5, output_tokens=7)
    return ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=cost, total_duration_ms=10,
                                total_input_tokens=5, total_output_tokens=7,
                                wall_duration_ms=wall, total_retries=1)


def _two_module_arch() -> ArchitectureSpec:
    auth = _module("Auth", LayerType.DOMAIN, "User")
    cart = _module("Cart", LayerType.APPLICATION, "Basket")
    return ArchitectureSpec(modules=(auth, cart), graph=ArchitectureGraph(edges={}))


def test_merge_implementations_concatenates_classes_and_aggregates_totals() -> None:
    arch = _two_module_arch()
    merged = ArchitectureMerger().merge_implementations(
        arch, (_impl(arch.modules[0], 0.25, 100), _impl(arch.modules[1], 0.5, 300)),
    )
    assert [c.class_name for c in merged.implemented_classes] == ["User", "Basket"]
    assert merged.total_cost_usd == 0.75
    assert merged.total_input_tokens == 10
    assert merged.wall_duration_ms == 300  # max across modules, not the sum
    assert merged.total_retries == 2


def test_merged_module_takes_first_module_identity_and_flattens_the_rest() -> None:
    merged = ArchitectureMerger().merge_implementations(_two_module_arch(), ())
    assert merged.module.name == "Auth"
    assert merged.module.layer is LayerType.DOMAIN
    assert merged.module.exports == ("User", "Basket")
    assert merged.module.invariants == ("Auth rule", "Cart rule")
    assert merged.module.depends == ()
    assert [c.name for c in merged.module.classes] == ["User", "Basket"]


def test_merge_with_no_modules_yields_synthetic_defaults() -> None:
    arch = ArchitectureSpec(modules=(), graph=ArchitectureGraph(edges={}))
    merged = ArchitectureMerger().merge_implementations(arch, ())
    assert merged.module.name == "Architecture"
    assert merged.module.layer is LayerType.DOMAIN
    assert merged.wall_duration_ms == 0


def test_merge_test_architectures_concatenates_in_order() -> None:
    sk = TestSkeleton(class_name="User", file_path="tests/test_user.py", code="")
    a = TestArchitecture(gherkin_scenarios=("s1",), test_skeletons=(sk,))
    b = TestArchitecture(gherkin_scenarios=("s2", "s3"), test_skeletons=())
    merged = ArchitectureMerger().merge_test_architectures((a, b))
    assert merged.gherkin_scenarios == ("s1", "s2", "s3")
    assert merged.test_skeletons == (sk,)
