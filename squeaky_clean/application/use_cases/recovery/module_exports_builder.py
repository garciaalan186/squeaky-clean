"""ModuleExportsBuilder: compute each module's EXPORTS list."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog


class ModuleExportsBuilder:
    """Derives EXPORTS: classes depended on from outside their module.

    A class must appear in its module's EXPORTS for another module's
    ``Module::Class`` dependency on it to validate. This scans every
    import edge and, whenever the source and target live in different
    modules, marks the target class exported from its own module.
    """

    def build(
        self, catalog: ClassCatalog, module_of: dict[str, str],
    ) -> dict[str, tuple[str, ...]]:
        """Return a module -> exported-class-names map."""
        exports: dict[str, list[str]] = {}
        for fqn, deps in catalog.import_graph.items():
            for dep in deps:
                if dep not in module_of or module_of[fqn] == module_of[dep]:
                    continue
                simple = dep.rsplit(".", 1)[-1]
                bucket = exports.setdefault(module_of[dep], [])
                if simple not in bucket:
                    bucket.append(simple)
        return {mod: tuple(names) for mod, names in exports.items()}
