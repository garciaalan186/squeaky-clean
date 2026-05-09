"""ModuleImplementation DTO: aggregated ICP results for one module."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class ModuleImplementation:
    """Immutable bundle returned by OrchestrateModule.

    Holds the source ``module`` spec, the tuple of ``implemented_classes``
    produced by ICPs, and accumulated cost / wall-clock across every ICP
    call made while realising the module.
    """

    module: ModuleSpec
    implemented_classes: tuple[ImplementedClass, ...]
    total_cost_usd: float
    total_duration_ms: int
    total_input_tokens: int
    total_output_tokens: int
    wall_duration_ms: int
    total_retries: int = 0
