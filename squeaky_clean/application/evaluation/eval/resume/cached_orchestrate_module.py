"""CachedOrchestrateModule: OrchestrateModule stand-in serving cached results."""

from __future__ import annotations

from squeaky_clean.application.generation.emission.module_implementation import (
    ModuleImplementation,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class CachedOrchestrateModule:
    """Stand-in for OrchestrateModule; returns cached ModuleImplementation."""

    def __init__(self, by_name: dict[str, ModuleImplementation]) -> None:
        self._by_name: dict[str, ModuleImplementation] = by_name

    def stamp_architecture(self, arch: ArchitectureSpec | None) -> None:
        del arch

    def execute(self, module: ModuleSpec) -> ModuleImplementation:
        return self._by_name[module.name]
