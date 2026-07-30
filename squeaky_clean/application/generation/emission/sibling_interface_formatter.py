"""SiblingInterfaceFormatter: emit SIBLING_INTERFACES block for an ICP prompt."""

from squeaky_clean.application.shared.language.dotted_path_resolver import DottedPathResolver
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class SiblingInterfaceFormatter:
    """Formats every non-focal class's fields and methods as a prompt block."""

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._resolver: DottedPathResolver = DottedPathResolver(toolkit)

    def format(
        self, module: ModuleSpec, focal_name: str,
        depends: tuple[str, ...] = (),
        architecture: ArchitectureSpec | None = None,
    ) -> str:
        """Block of only the siblings the focal class DECLARES a relation with
        (``depends`` ∪ its own depends/implements/concretes); no declared deps
        → empty block (an empty ``depends`` injected the whole module pre-R3.2).
        """
        dep_set = self._dependency_set(module, focal_name, depends)
        lines: list[str] = ["SIBLING_INTERFACES"]
        seen: set[str] = {focal_name}
        for cls in module.classes:
            if cls.name in seen:
                continue
            if cls.name not in dep_set:
                continue
            lines.append(self._format_one(cls, module, architecture))
            seen.add(cls.name)
        if architecture is not None:
            for sibling_module in architecture.modules:
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
                    lines.append(
                        self._format_one(cls, module, architecture),
                    )
                    seen.add(cls.name)
        return "\n".join(lines)

    def _dependency_set(
        self, module: ModuleSpec, focal_name: str, depends: tuple[str, ...],
    ) -> set[str]:
        """Names the focal class declares a relationship with (deps only)."""
        names = {d.split("::", 1)[1] if "::" in d else d for d in depends}
        focal = next((c for c in module.classes if c.name == focal_name), None)
        if focal is not None:
            names.update(focal.depends)
            names.update(focal.concretes)
            if focal.implements:
                names.add(focal.implements)
        return names

    def _format_one(
        self, cls: ClassSpec, module: ModuleSpec,
        architecture: ArchitectureSpec | None,
    ) -> str:
        path = self._resolver.resolve(cls.name, module, architecture)
        fields = ", ".join(cls.fields) if cls.fields else ""
        methods = ", ".join(cls.methods) if cls.methods else ""
        invariants = ", ".join(f'"{i}"' for i in cls.invariants)
        return (
            f"{cls.name} ({cls.pattern}, file={path}): "
            f"fields=[{fields}], methods=[{methods}], "
            f"invariants=[{invariants}]"
        )
