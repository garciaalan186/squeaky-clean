"""ArchitectureSpec entity: top-level multi-module architecture container."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class ArchitectureSpec:
    """Immutable container for one or more ModuleSpecs plus their dep graph.

    Single-module mode keeps `modules` as a 1-tuple and `graph.edges` empty;
    this is backward-compatible with the legacy single-ModuleSpec pipeline.
    """

    modules: tuple[ModuleSpec, ...]
    graph: ArchitectureGraph

    def validate(self) -> tuple[str, ...]:
        """Return tuple of violations: empty modules, cycles, unknown deps."""
        violations: list[str] = []
        if not self.modules:
            violations.append("no modules declared")
        names = {m.name for m in self.modules}
        all_classes = {c.name for m in self.modules for c in m.classes}
        all_exports = {e for m in self.modules for e in m.exports}
        for src, deps in self.graph.edges.items():
            if src not in names:
                violations.append(f"graph edge from unknown module {src!r}")
            for dep in deps:
                if dep not in names:
                    violations.append(
                        f"module {src!r} depends on unknown module {dep!r}"
                    )
        violations.extend(
            f"cycle: {c}" for c in self.graph.cycle_violations()
        )
        for module in self.modules:
            violations.extend(self._validate_module(module, all_classes, all_exports))
        return tuple(violations)

    def _validate_module(
        self, module: object, all_classes: set[str], all_exports: set[str],
    ) -> list[str]:
        """Validate one module, accepting cross-module exported classes."""
        from squeaky_clean.domain.entities.module_spec import ModuleSpec
        if not isinstance(module, ModuleSpec):
            return []
        violations: list[str] = []
        if not module.name:
            violations.append("module name is empty")
        if not module.classes:
            violations.append(f"module {module.name!r} declares zero classes")
        local = {c.name for c in module.classes}
        for cls in module.classes:
            for dep in cls.depends:
                bare = dep.split("::", 1)[1] if "::" in dep else dep
                known_local = bare in local
                known_exported = bare in all_exports and bare in all_classes
                if not (known_local or known_exported):
                    violations.append(
                        f"{cls.name} depends on unknown class {dep}"
                    )
            for entry in cls.fields:
                if ":" not in entry:
                    violations.append(
                        f"{cls.name} field {entry!r} missing 'name: Type'"
                    )
        return violations

    @classmethod
    def single(cls, module: ModuleSpec) -> ArchitectureSpec:
        """Build an ArchitectureSpec wrapping one module, no edges."""
        return cls(
            modules=(module,),
            graph=ArchitectureGraph(edges={}),
        )
