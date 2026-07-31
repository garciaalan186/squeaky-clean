"""Tests for ResumeStubFactory: cached-stage stubbing and cost seeding."""

from dataclasses import replace

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.resume_stub_factory import ResumeStubFactory
from squeaky_clean.application.evaluation.eval.resume.resume_stubs import (
    CachedDesignArchitecture,
    CachedOrchestrateModule,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _impl() -> ModuleImplementation:
    cls = ClassSpec(name="Operand", pattern="ValueObject", implements=None,
                    methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(cls,), invariants=())
    ic = ImplementedClass(class_name="Operand", file_path="src/operand.py",
                          code="class Operand: ...", test_code=None,
                          cost_usd=0.1, duration_ms=100,
                          input_tokens=10, output_tokens=20)
    return ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=0.1, total_duration_ms=100,
                                total_input_tokens=10, total_output_tokens=20,
                                wall_duration_ms=0)


def _build(deps: RunEvalDependencies, impl: ModuleImplementation) -> RunEvalDependencies:
    arch = ArchitectureSpec(modules=(impl.module,), graph=ArchitectureGraph(edges={}))
    empty = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    return ResumeStubFactory().build(deps, arch, empty, empty, (impl,),
                                     prior_cost_usd=1.25)


def test_prior_cost_usd_seeds_cost_gate() -> None:
    """R0.5 guard: a resumed run must not silently reset its budget to $0."""
    gate = CostGate()
    deps = replace(build_stub_deps(), cost_gate=gate)
    _build(deps, _impl())
    assert gate.spent_usd() == pytest.approx(1.25)


def test_build_without_cost_gate_does_not_crash() -> None:
    deps = build_stub_deps()
    assert deps.cost_gate is None
    new_deps = _build(deps, _impl())
    assert isinstance(new_deps.design_architecture, CachedDesignArchitecture)


def test_build_replaces_cached_stages_and_keeps_original_deps() -> None:
    """Stubs answer from cache; the input deps bundle is left untouched."""
    deps = build_stub_deps()
    impl = _impl()
    new_deps = _build(deps, impl)
    assert isinstance(new_deps.orchestrate_module, CachedOrchestrateModule)
    # Cached stages answer without any LLM call, keyed by module name.
    assert new_deps.orchestrate_module.execute(impl.module) is impl
    arch = new_deps.design_architecture.execute(P0)
    assert arch.modules == (impl.module,)
    # replace() returned a new bundle; the original mocks are still wired.
    assert new_deps is not deps
    assert deps.design_architecture is not new_deps.design_architecture
