"""Tests for CachedOrchestrateModule (cached stand-in, no LLM call)."""

from squeaky_clean.application.evaluation.eval.resume.cached_orchestrate_module import (
    CachedOrchestrateModule,
)
from squeaky_clean.application.generation.emission.module_implementation import (
    ModuleImplementation,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def test_cached_orchestrate_module_looks_up_by_name() -> None:
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    impl = ModuleImplementation(module=module, implemented_classes=(),
                                total_cost_usd=0.0, total_duration_ms=0,
                                total_input_tokens=0, total_output_tokens=0,
                                wall_duration_ms=0)
    stub = CachedOrchestrateModule({"Calculator": impl})
    stub.stamp_architecture(None)  # accepted no-op, mirrors OrchestrateModule
    assert stub.execute(module) is impl
