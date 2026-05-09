"""Unit tests for OrchestrateArchitecture toposort + fan-out."""

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class _FakeOrchestrator:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.stamped: object = None

    def stamp_architecture(self, architecture: object) -> None:
        self.stamped = architecture

    def execute(self, module: ModuleSpec) -> ModuleImplementation:
        self.calls.append(module.name)
        return ModuleImplementation(
            module=module, implemented_classes=(),
            total_cost_usd=0.0, total_duration_ms=0,
            total_input_tokens=0, total_output_tokens=0,
            wall_duration_ms=0, total_retries=0,
        )


def _module(name: str) -> ModuleSpec:
    cls = ClassSpec(
        name=f"{name}Class", pattern="SimpleClass",
        fields=(), methods=(), depends=(), concretes=(),
        invariants=(), implements=None,
    )
    return ModuleSpec(
        name=name, layer=LayerType.DOMAIN,
        exports=(f"{name}Class",), depends=(),
        classes=(cls,), invariants=(),
    )


def test_single_module_runs_once() -> None:
    fake = _FakeOrchestrator()
    arch = ArchitectureSpec.single(_module("Cart"))
    out = OrchestrateArchitecture(fake).execute(arch)  # type: ignore[arg-type]
    assert len(out) == 1
    assert fake.calls == ["Cart"]


def test_two_independent_modules_both_run() -> None:
    fake = _FakeOrchestrator()
    arch = ArchitectureSpec(
        modules=(_module("Cart"), _module("Catalog")),
        graph=ArchitectureGraph(edges={}),
    )
    out = OrchestrateArchitecture(fake).execute(arch)  # type: ignore[arg-type]
    assert len(out) == 2
    assert set(fake.calls) == {"Cart", "Catalog"}


def test_toposort_runs_dependency_first() -> None:
    fake = _FakeOrchestrator()
    arch = ArchitectureSpec(
        modules=(_module("Cart"), _module("Catalog")),
        graph=ArchitectureGraph(edges={"Cart": ("Catalog",)}),
    )
    OrchestrateArchitecture(fake).execute(arch)  # type: ignore[arg-type]
    assert fake.calls.index("Catalog") < fake.calls.index("Cart")
