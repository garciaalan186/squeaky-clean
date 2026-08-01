"""Tests for CachedGenerateSecurityTests (per-arch once gate)."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.cached_generate_security_tests import (
    CachedGenerateSecurityTests,
)
from squeaky_clean.application.generation.security.security_review import SecurityReview
from squeaky_clean.application.generation.security.security_test_context import (
    SecurityTestContext,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(name: str) -> ModuleSpec:
    return ModuleSpec(name=name, layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(), invariants=())


def test_cached_generate_security_tests_gates_on_first_module() -> None:
    first, second = _module("Auth"), _module("Cart")
    arch = ArchitectureSpec(modules=(first, second),
                            graph=ArchitectureGraph(edges={}))
    cached = TestArchitecture(gherkin_scenarios=("Feature: sec",), test_skeletons=())
    stub = CachedGenerateSecurityTests(cached, arch)
    review = SecurityReview(concerns=())
    ctx_first = SecurityTestContext(review=review, module=first, problem=P0)
    ctx_second = SecurityTestContext(review=review, module=second, problem=P0)
    assert stub.execute(ctx_first) is cached
    assert stub.execute(ctx_second).gherkin_scenarios == ()
