"""SquibDependsRenderer: render a class's intra-architecture dependencies."""

from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog


class SquibDependsRenderer:
    """Renders one class's import edges as Squib `depends:` entries.

    A dependency on a class in the same module is rendered bare
    (``Order``); one in another module is rendered ``Module::Class`` so the
    cross-module validator can check the target's EXPORTS. Only edges that
    resolve to a catalogued (assigned) class are emitted; order preserved.
    The catalog and module assignment are per-renderer state.
    """

    def __init__(self, catalog: ClassCatalog, module_of: dict[str, str]) -> None:
        self._catalog: ClassCatalog = catalog
        self._module_of: dict[str, str] = module_of

    def render(self, fqn: str) -> tuple[str, ...]:
        """Return the deduplicated `depends:` entries for one class FQN."""
        own = self._module_of[fqn]
        out: list[str] = []
        for dep in self._catalog.import_graph.get(fqn, ()):
            if dep not in self._module_of:
                continue
            simple = dep.rsplit(".", 1)[-1]
            ref = simple if self._module_of[dep] == own else f"{self._module_of[dep]}::{simple}"
            if ref not in out:
                out.append(ref)
        return tuple(out)
