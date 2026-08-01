"""Tests for CachedGenerateTestArchitecture (per-arch once gate)."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.cached_generate_test_architecture import (
    CachedGenerateTestArchitecture,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(name: str) -> ModuleSpec:
    return ModuleSpec(name=name, layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(), invariants=())


def test_cached_generate_test_architecture_gates_on_first_module() -> None:
    first, second = _module("Auth"), _module("Cart")
    arch = ArchitectureSpec(modules=(first, second),
                            graph=ArchitectureGraph(edges={}))
    cached = TestArchitecture(gherkin_scenarios=("Feature: y",), test_skeletons=())
    stub = CachedGenerateTestArchitecture(cached, arch)
    assert stub.execute(TestArchitectureContext(module=first, problem=P0)) is cached
    rest = stub.execute(TestArchitectureContext(module=second, problem=P0))
    assert rest.gherkin_scenarios == ()
