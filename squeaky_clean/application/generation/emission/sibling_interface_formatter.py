"""SiblingInterfaceFormatter: emit SIBLING_INTERFACES block for an ICP prompt."""

from squeaky_clean.application.shared.language.dotted_path_resolver import DottedPathResolver
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class SiblingInterfaceFormatter:
    """Formats every non-focal class's fields and methods as a prompt block."""

    def __init__(
        self, toolkit: LanguageToolkit,
        architecture: ArchitectureSpec | None = None,
    ) -> None:
        self._arch: ArchitectureSpec | None = architecture
        self._resolver: DottedPathResolver = DottedPathResolver(toolkit, architecture)

    def format(self, module: ModuleSpec, focal: ClassSpec) -> str:
        """Block of only the siblings the focal class DECLARES a relation with
        (its depends/implements/concretes plus the module entry's); no declared
        deps → empty block (an empty set injected the whole module pre-R3.2).
        """
        dep_set = self._dependency_set(module, focal)
        lines: list[str] = ["SIBLING_INTERFACES"]
        seen: set[str] = {focal.name}
        for cls in module.classes:
            if cls.name in seen:
                continue
            if cls.name not in dep_set:
                continue
            lines.append(self._format_one(cls, module))
            seen.add(cls.name)
        if self._arch is not None:
            for sibling_module in self._arch.modules:
                if sibling_module.name == module.name:
                    continue
                exported = set(sibling_module.exports)
                for cls in sibling_module.classes:
                    if cls.name in seen:
                        continue
                    if cls.name not in exported:
                        continue
                    if cls.name not in dep_set:
                        continue
                    lines.append(self._format_one(cls, module))
                    seen.add(cls.name)
        return "\n".join(lines)

    def _dependency_set(self, module: ModuleSpec, focal: ClassSpec) -> set[str]:
        """Names the focal class declares a relationship with (deps only)."""
        names = {d.split("::", 1)[1] if "::" in d else d for d in focal.depends}
        for cls in (focal, *(c for c in module.classes if c.name == focal.name)):
            names.update(cls.depends)
            names.update(cls.concretes)
            if cls.implements:
                names.add(cls.implements)
        return names

    def _format_one(self, cls: ClassSpec, module: ModuleSpec) -> str:
        path = self._resolver.resolve(cls.name, module)
        fields = ", ".join(cls.fields) if cls.fields else ""
        methods = ", ".join(cls.methods) if cls.methods else ""
        invariants = ", ".join(f'"{i}"' for i in cls.invariants)
        return (
            f"{cls.name} ({cls.pattern}, file={path}): "
            f"fields=[{fields}], methods=[{methods}], "
            f"invariants=[{invariants}]"
        )
