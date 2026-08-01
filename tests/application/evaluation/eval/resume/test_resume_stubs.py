"""Tests for resume_stubs: cached stand-ins that answer without any LLM call."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.resume_stubs import (
    CachedDesignArchitecture,
    CachedGenerateTestArchitecture,
    CachedOrchestrateModule,
    CachedReviewSecurity,
)
from squeaky_clean.application.generation.emission.module_implementation import (
    ModuleImplementation,
)
from squeaky_clean.application.generation.security.security_review import SecurityReview
from squeaky_clean.application.generation.security.security_review_context import (
    SecurityReviewContext,
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


def _arch(*modules: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(modules=modules, graph=ArchitectureGraph(edges={}))


def test_cached_design_architecture_ignores_problem() -> None:
    arch = _arch(_module("Calculator"))
    stub = CachedDesignArchitecture(arch)
    assert stub.execute(P0) is arch
    assert stub.last_raw_notation == ""


def test_cached_generate_test_architecture_gates_on_first_module() -> None:
    first, second = _module("Auth"), _module("Cart")
    cached = TestArchitecture(gherkin_scenarios=("Feature: y",), test_skeletons=())
    stub = CachedGenerateTestArchitecture(cached, _arch(first, second))
    assert stub.execute(TestArchitectureContext(module=first, problem=P0)) is cached
    rest = stub.execute(TestArchitectureContext(module=second, problem=P0))
    assert rest.gherkin_scenarios == ()


def test_cached_review_security_returns_injected_review() -> None:
    review = SecurityReview(concerns=())
    stub = CachedReviewSecurity(review)
    ctx = SecurityReviewContext(module=_module("Auth"), problem=P0)
    assert stub.execute(ctx) is review


def test_cached_orchestrate_module_looks_up_by_name() -> None:
    module = _module("Calculator")
    impl = ModuleImplementation(module=module, implemented_classes=(),
                                total_cost_usd=0.0, total_duration_ms=0,
                                total_input_tokens=0, total_output_tokens=0,
                                wall_duration_ms=0)
    stub = CachedOrchestrateModule({"Calculator": impl})
    stub.stamp_architecture(None)  # accepted no-op, mirrors OrchestrateModule
    assert stub.execute(module) is impl
