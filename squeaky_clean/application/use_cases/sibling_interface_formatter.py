"""SiblingInterfaceFormatter: emit SIBLING_INTERFACES block for an ICP prompt."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.dotted_path_resolver import DottedPathResolver
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class SiblingInterfaceFormatter:
    """Formats every non-focal class's fields and methods as a prompt block."""

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._resolver: DottedPathResolver = DottedPathResolver(toolkit)

    def format(
        self,
        module: ModuleSpec,
        focal_name: str,
        depends: tuple[str, ...] = (),
        architecture: ArchitectureSpec | None = None,
    ) -> str:
        """Return a SIBLING_INTERFACES block for the focal class's dependencies.

        When ``depends`` is non-empty, only siblings whose name appears
        in ``depends`` are included. Both intra-module siblings AND
        cross-module exported classes (when ``architecture`` is supplied)
        are eligible. Class names are globally unique within an
        ArchitectureSpec, so a single name lookup resolves correctly.
        """
        dep_set = {d.split("::", 1)[1] if "::" in d else d for d in depends}
        lines: list[str] = ["SIBLING_INTERFACES"]
        seen: set[str] = {focal_name}
        for cls in module.classes:
            if cls.name in seen:
                continue
            if dep_set and cls.name not in dep_set:
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
                    if dep_set and cls.name not in dep_set:
                        continue
                    lines.append(
                        self._format_one(cls, module, architecture),
                    )
                    seen.add(cls.name)
        return "\n".join(lines)

    def _format_one(
        self,
        cls: ClassSpec,
        module: ModuleSpec,
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
