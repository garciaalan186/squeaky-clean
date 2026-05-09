"""OrchestrateArchitecture: fan-out ArchitectureSpec → ModuleImplementations."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_MAX_PARALLEL_MODULES: int = 4


class OrchestrateArchitecture:
    """Run OrchestrateModule per ModuleSpec; merge results in dependency order.

    The result is a tuple of ModuleImplementation in topological-sorted
    order (modules with no incoming edges first). Cycles are blocked at
    the spec layer (ArchitectureSpec.validate()) so this orchestrator
    can assume a DAG.
    """

    def __init__(self, single: OrchestrateModule) -> None:
        self._single: OrchestrateModule = single

    def register_tech_specs(self, specs: tuple[TechSpec, ...]) -> None:
        """Register resolved TechSpecs for Tier C ICP injection (H1)."""
        for s in specs:
            self._single.register_tech_spec(s)

    def execute(
        self, arch: ArchitectureSpec,
    ) -> tuple[ModuleImplementation, ...]:
        """Dispatch each module's ICPs in parallel; return module impls."""
        ordered = self._toposort(arch)
        self._single.stamp_architecture(arch)
        with ThreadPoolExecutor(max_workers=_MAX_PARALLEL_MODULES) as pool:
            results = list(pool.map(self._single.execute, ordered))
        return tuple(results)

    def _toposort(
        self, arch: ArchitectureSpec,
    ) -> list:  # type: ignore[type-arg]
        order: list[str] = []
        seen: set[str] = set()

        def visit(name: str) -> None:
            if name in seen:
                return
            seen.add(name)
            for dep in arch.graph.edges.get(name, ()):
                visit(dep)
            order.append(name)

        for m in arch.modules:
            visit(m.name)
        by_name = {m.name: m for m in arch.modules}
        return [by_name[n] for n in order if n in by_name]
