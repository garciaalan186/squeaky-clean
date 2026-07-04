"""ArchitectureSpec entity: top-level multi-module architecture container."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.rules.architecture_spec_rules import collect_violations


@dataclass(frozen=True)
class ArchitectureSpec:
    """Immutable container for one or more ModuleSpecs plus their dep graph.

    Single-module mode keeps `modules` as a 1-tuple and `graph.edges` empty;
    this is backward-compatible with the legacy single-ModuleSpec pipeline.
    Validation logic lives in `squeaky_clean.domain.rules.architecture_spec_rules`.
    """

    modules: tuple[ModuleSpec, ...]
    graph: ArchitectureGraph

    def validate(self) -> tuple[str, ...]:
        """Return tuple of violations from architecture_spec_rules."""
        return tuple(collect_violations(self))

    @classmethod
    def single(cls, module: ModuleSpec) -> ArchitectureSpec:
        """Build an ArchitectureSpec wrapping one module, no edges."""
        return cls(modules=(module,), graph=ArchitectureGraph(edges={}))
