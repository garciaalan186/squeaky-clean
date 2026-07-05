"""FrameworkCouplingTransform: split coupled classes 1->N across layers."""

from squeaky_clean.application.use_cases.recovery.clean_split_factory import (
    CleanSplitFactory,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class FrameworkCouplingTransform:
    """Rewrites the spec, splitting each target class into Entity+Repo+Adapter.

    In the target's module the class becomes a pure Entity plus a Repository
    port (both exported); the framework Adapter moves to a companion
    ``<Module>Infra`` Infrastructure module that depends inward on them. The
    result parses and validates on the greenfield path. Deterministic.
    """

    def __init__(self) -> None:
        self._factory: CleanSplitFactory = CleanSplitFactory()

    def apply(
        self, spec: ArchitectureSpec, targets: frozenset[str],
    ) -> ArchitectureSpec:
        """Return a new spec with every ``targets`` class split 1->N."""
        modules: list[ModuleSpec] = []
        edges = {m.name: spec.graph.edges.get(m.name, ()) for m in spec.modules}
        for module in spec.modules:
            domain, infra = self._split_module(module, targets)
            modules.append(domain)
            if infra is not None:
                modules.append(infra)
                edges[infra.name] = (module.name,)
        return ArchitectureSpec(
            modules=tuple(modules), graph=ArchitectureGraph(edges=edges),
        )

    def _split_module(
        self, module: ModuleSpec, targets: frozenset[str],
    ) -> tuple[ModuleSpec, ModuleSpec | None]:
        kept: list[ClassSpec] = []
        adapters: list[ClassSpec] = []
        exports = list(module.exports)
        for cls in module.classes:
            if cls.name not in targets:
                kept.append(cls)
                continue
            kept.append(self._factory.entity(cls))
            kept.append(self._factory.repository(cls))
            adapters.append(self._factory.adapter(cls, module.name))
            exports.extend(n for n in (cls.name, f"{cls.name}Repository")
                           if n not in exports)
        domain = ModuleSpec(
            name=module.name, layer=module.layer, exports=tuple(exports),
            depends=module.depends, classes=tuple(kept), invariants=module.invariants,
        )
        return domain, self._infra(module.name, tuple(adapters))

    def _infra(self, module: str, adapters: tuple[ClassSpec, ...]) -> ModuleSpec | None:
        if not adapters:
            return None
        depends = tuple(dict.fromkeys(d for a in adapters for d in a.depends))
        return ModuleSpec(
            name=f"{module}Infra", layer=LayerType.INFRASTRUCTURE, exports=(),
            depends=depends, classes=adapters, invariants=(),
        )
