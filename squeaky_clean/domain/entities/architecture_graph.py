"""ArchitectureGraph entity: DAG of cross-module dependencies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureGraph:
    """Immutable directed graph of module-name -> tuple of dependency module names.

    Validates against cycles. Used to gate multi-module pipelines before
    dispatching ICPs (per ROADMAP §C2). Module names are matched verbatim
    against `ModuleSpec.name` for whichever module the edge originates from.
    """

    edges: dict[str, tuple[str, ...]]

    def cycle_violations(self) -> tuple[str, ...]:
        """Return non-empty tuple of cycle descriptions iff cycles exist."""
        white: set[str] = set(self.edges.keys())
        gray: set[str] = set()
        black: set[str] = set()
        cycles: list[str] = []
        path: list[str] = []
        for node in list(white):
            if node in black:
                continue
            self._visit(node, white, gray, black, path, cycles)
        return tuple(cycles)

    def is_dag(self) -> bool:
        """True iff this graph has no cycles."""
        return not self.cycle_violations()

    def _visit(
        self,
        node: str,
        white: set[str],
        gray: set[str],
        black: set[str],
        path: list[str],
        cycles: list[str],
    ) -> None:
        if node in black:
            return
        if node in gray:
            i = path.index(node) if node in path else 0
            cycles.append(" -> ".join(path[i:] + [node]))
            return
        white.discard(node)
        gray.add(node)
        path.append(node)
        for child in self.edges.get(node, ()):
            self._visit(child, white, gray, black, path, cycles)
        path.pop()
        gray.discard(node)
        black.add(node)
