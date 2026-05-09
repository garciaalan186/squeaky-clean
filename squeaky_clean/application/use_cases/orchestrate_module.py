"""OrchestrateModule: EM-level use case that produces a ModuleImplementation."""

import time

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.parallel_icp_dispatcher import ParallelICPDispatcher
from squeaky_clean.application.use_cases.port_method_decomposer import (
    decompose_module_for_tier_c,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class OrchestrateModule:
    """Deterministic EM: assigns ICPs and dispatches them in parallel."""

    def __init__(
        self,
        implement_class: ImplementClass,
        assigner: AssignPatterns,
    ) -> None:
        self._assigner: AssignPatterns = assigner
        self._dispatcher: ParallelICPDispatcher = ParallelICPDispatcher(
            implement_class
        )

    def stamp_architecture(
        self, architecture: ArchitectureSpec | None,
    ) -> None:
        """Stamp the architecture so cross-module siblings reach ICP prompts."""
        self._assigner.with_architecture(architecture)

    def register_tech_spec(self, spec: TechSpec) -> None:
        """Register a TechSpec for Tier C infrastructure-adapter ICPs (H1)."""
        self._assigner.register_tech_spec(spec)

    def execute(self, module: ModuleSpec) -> ModuleImplementation:
        """Assign ICPs for every class in ``module`` and dispatch them."""
        if module.layer is LayerType.INFRASTRUCTURE:
            module = decompose_module_for_tier_c(
                module, self._assigner.tier_c_class_names(module),
            )
        assignments = self._assigner.assign_all(module)
        t0 = time.monotonic()
        results = self._dispatcher.dispatch(assignments)
        wall_ms = int((time.monotonic() - t0) * 1000)
        return self._build(module, results, wall_ms)

    def _build(
        self,
        module: ModuleSpec,
        results: tuple[ImplementedClass, ...],
        wall_ms: int = 0,
    ) -> ModuleImplementation:
        total_cost = sum(r.cost_usd for r in results)
        total_ms = sum(r.duration_ms for r in results)
        total_in = sum(r.input_tokens for r in results)
        total_out = sum(r.output_tokens for r in results)
        total_retries = sum(r.retries for r in results)
        return ModuleImplementation(
            module=module,
            implemented_classes=results,
            total_cost_usd=total_cost,
            total_duration_ms=total_ms,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            wall_duration_ms=wall_ms,
            total_retries=total_retries,
        )
