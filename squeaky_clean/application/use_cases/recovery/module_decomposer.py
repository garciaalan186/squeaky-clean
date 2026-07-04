"""ModuleDecomposer: turn a ClassCatalog + layers into an ArchitectureSpec."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.use_cases.recovery.class_spec_builder import ClassSpecBuilder
from squeaky_clean.application.use_cases.recovery.domain_scc_finder import DomainSCCFinder
from squeaky_clean.application.use_cases.recovery.module_assigner import ModuleAssigner
from squeaky_clean.application.use_cases.recovery.module_exports_builder import (
    ModuleExportsBuilder,
)
from squeaky_clean.application.use_cases.recovery.module_graph_builder import (
    ModuleGraphBuilder,
)
from squeaky_clean.application.use_cases.recovery.squib_depends_renderer import (
    SquibDependsRenderer,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class ModuleDecomposer:
    """Stage 4: assemble a validated ArchitectureSpec from the catalog.

    Domain SCCs seed modules; non-domain classes attach to the modules
    they depend on; class dependencies, EXPORTS, module DEPENDS, and the
    module DAG are rendered so the result parses and validates on the
    greenfield path. Fully deterministic — no LLM participates.
    """

    def __init__(self) -> None:
        self._scc: DomainSCCFinder = DomainSCCFinder()
        self._assigner: ModuleAssigner = ModuleAssigner()
        self._depends: SquibDependsRenderer = SquibDependsRenderer()
        self._classes: ClassSpecBuilder = ClassSpecBuilder()
        self._exports: ModuleExportsBuilder = ModuleExportsBuilder()
        self._graph: ModuleGraphBuilder = ModuleGraphBuilder()

    def decompose(
        self, catalog: ClassCatalog, layers: dict[str, LayerType],
    ) -> ArchitectureSpec:
        """Return the ArchitectureSpec recovered from catalog + layers."""
        asg = self._assigner.assign(catalog, layers, self._scc.components(catalog, layers))
        exports = self._exports.build(catalog, asg.module_of)
        depends, edges = self._graph.build(catalog, asg.module_of)
        grouped = self._group(catalog, asg.module_of)
        modules = tuple(
            ModuleSpec(
                name=mod, layer=asg.layer_of[mod],
                exports=exports.get(mod, ()), depends=depends.get(mod, ()),
                classes=tuple(specs), invariants=(),
            )
            for mod, specs in sorted(grouped.items())
        )
        return ArchitectureSpec(modules=modules, graph=ArchitectureGraph(edges=edges))

    def _group(
        self, catalog: ClassCatalog, module_of: dict[str, str],
    ) -> dict[str, list[ClassSpec]]:
        grouped: dict[str, list[ClassSpec]] = {}
        for record in catalog.classes:
            depends = self._depends.render(record.fqn, catalog, module_of)
            spec = self._classes.build(record, depends)
            grouped.setdefault(module_of[record.fqn], []).append(spec)
        return grouped
