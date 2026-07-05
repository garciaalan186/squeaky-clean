"""SquibDependsRenderer: render a class's intra-architecture dependencies."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog


class SquibDependsRenderer:
    """Renders one class's import edges as Squib `depends:` entries.

    A dependency on a class in the same module is rendered bare
    (``Order``); one in another module is rendered ``Module::Class`` so the
    cross-module validator can check the target's EXPORTS. Only edges that
    resolve to a catalogued (assigned) class are emitted; order preserved.
    """

    def render(
        self, fqn: str, catalog: ClassCatalog, module_of: dict[str, str],
    ) -> tuple[str, ...]:
        """Return the deduplicated `depends:` entries for one class FQN."""
        own = module_of[fqn]
        out: list[str] = []
        for dep in catalog.import_graph.get(fqn, ()):
            if dep not in module_of:
                continue
            simple = dep.rsplit(".", 1)[-1]
            ref = simple if module_of[dep] == own else f"{module_of[dep]}::{simple}"
            if ref not in out:
                out.append(ref)
        return tuple(out)
