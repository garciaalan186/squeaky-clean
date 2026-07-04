"""ModuleAssigner: place every catalogued class into a named module."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.module_assignment import ModuleAssignment
from squeaky_clean.domain.value_objects.layer_type import LayerType


class ModuleAssigner:
    """Groups classes into modules: domain SCCs first, then attachment.

    Each domain SCC becomes a DOMAIN module named after its representative
    class. Every non-domain class attaches to the domain module it depends
    on most; a class with no domain dependency becomes its own module in
    its own layer. Module names are made unique deterministically.
    """

    def assign(
        self,
        catalog: ClassCatalog,
        layers: dict[str, LayerType],
        components: tuple[tuple[str, ...], ...],
    ) -> ModuleAssignment:
        """Return the FQN -> module and module -> layer assignment."""
        module_of: dict[str, str] = {}
        layer_of: dict[str, LayerType] = {}
        taken: set[str] = set()
        for comp in components:
            name = self._unique(comp[0].rsplit(".", 1)[-1], taken)
            layer_of[name] = LayerType.DOMAIN
            for fqn in comp:
                module_of[fqn] = name
        for record in catalog.classes:
            if layers[record.fqn] is LayerType.DOMAIN:
                continue
            self._attach(record.fqn, catalog, module_of, layer_of, layers, taken)
        return ModuleAssignment(module_of=module_of, layer_of=layer_of)

    def _attach(
        self,
        fqn: str,
        catalog: ClassCatalog,
        module_of: dict[str, str],
        layer_of: dict[str, LayerType],
        layers: dict[str, LayerType],
        taken: set[str],
    ) -> None:
        target = self._target(fqn, catalog, module_of)
        if target is None:
            target = self._unique(fqn.rsplit(".", 1)[-1], taken)
            layer_of[target] = layers[fqn]
        module_of[fqn] = target

    def _target(
        self, fqn: str, catalog: ClassCatalog, module_of: dict[str, str],
    ) -> str | None:
        counts: dict[str, int] = {}
        for dep in catalog.import_graph.get(fqn, ()):
            mod = module_of.get(dep)
            if mod is not None:
                counts[mod] = counts.get(mod, 0) + 1
        if not counts:
            return None
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    def _unique(self, base: str, taken: set[str]) -> str:
        name = base
        suffix = 2
        while name in taken:
            name = f"{base}{suffix}"
            suffix += 1
        taken.add(name)
        return name
