"""ModuleGraphBuilder: compute module DEPENDS and the module DAG edges."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog

_Graph = tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]


class ModuleGraphBuilder:
    """Derives cross-module DEPENDS entries and the module dependency DAG.

    For every import edge crossing a module boundary it records a
    ``Module::Class`` entry under the source module and a module-level
    edge. The returned edge map keys every module (empty tuple when it
    depends on nothing) to match the parser's canonical graph form.
    """

    def build(self, catalog: ClassCatalog, module_of: dict[str, str]) -> _Graph:
        """Return (module -> DEPENDS entries, module -> dependency modules)."""
        depends: dict[str, list[str]] = {}
        edges: dict[str, list[str]] = {}
        for fqn, deps in catalog.import_graph.items():
            src = module_of[fqn]
            for dep in deps:
                if dep not in module_of or module_of[dep] == src:
                    continue
                tgt = module_of[dep]
                self._add(depends.setdefault(src, []), f"{tgt}::{dep.rsplit('.', 1)[-1]}")
                self._add(edges.setdefault(src, []), tgt)
        keyed = {m: tuple(edges.get(m, [])) for m in sorted(set(module_of.values()))}
        return {m: tuple(v) for m, v in depends.items()}, keyed

    def _add(self, bucket: list[str], value: str) -> None:
        if value not in bucket:
            bucket.append(value)
