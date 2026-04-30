"""SecurityConcernFormatter: format one SecurityConcern into an ICP user prompt."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.use_cases.dotted_path_resolver import DottedPathResolver
from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class SecurityConcernFormatter:
    """Renders one SecurityConcern + ClassSpec into a Security ICP user prompt."""

    def __init__(
        self,
        toolkit: LanguageToolkit | None = None,
        module: ModuleSpec | None = None,
        architecture: ArchitectureSpec | None = None,
    ) -> None:
        self._toolkit: LanguageToolkit | None = toolkit
        self._module: ModuleSpec | None = module
        self._architecture: ArchitectureSpec | None = architecture
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._camel: PascalToCamelConverter = PascalToCamelConverter()
        self._resolver: DottedPathResolver | None = (
            DottedPathResolver(toolkit) if toolkit is not None else None
        )

    def format(self, concern: SecurityConcern, cls: ClassSpec) -> str:
        """Return a compact plain-text prompt for the Security ICP."""
        fields = ", ".join(cls.fields) if cls.fields else "(none)"
        methods = ", ".join(cls.methods) if cls.methods else "(none)"
        target_file = self._dotted_or_stem(concern.target_class)
        lines: list[str] = [
            f"CONCERN {concern.category}",
            f"TARGET_CLASS {concern.target_class}",
            f"TARGET_FILE {target_file}",
            f"DESCRIPTION {concern.description}",
            f"TEST_SCENARIO {concern.test_scenario}",
            f"TARGET_FIELDS [{fields}]",
            f"TARGET_METHODS [{methods}]",
        ]
        depends_files = self._depends_files(cls)
        if depends_files:
            lines.append(f"DEPENDS_FILES {depends_files}")
        return "\n".join(lines)

    def _dotted_or_stem(self, class_name: str) -> str:
        """Return dotted path when module+toolkit known, else bare stem."""
        if self._resolver is not None and self._module is not None:
            return self._resolver.resolve(
                class_name, self._module, self._architecture,
            )
        return self._stem(class_name)

    def _stem(self, class_name: str) -> str:
        """Convert class name to file stem using the toolkit's case convention."""
        if self._toolkit is not None:
            if self._toolkit.identifier_case == "snake":
                return self._snake.convert(class_name)
            if self._toolkit.identifier_case == "pascal":
                return class_name
            return self._camel.convert(class_name)
        return self._snake_fallback(class_name)

    def _depends_files(self, cls: ClassSpec) -> str:
        """Return 'ClassName=<dotted_path_or_stem>' pairs for each dependency.

        Strips any 'Module::' qualifier so the emitted reference matches
        the canonical class name.
        """
        if not cls.depends:
            return ""
        pairs: list[str] = []
        for dep in cls.depends:
            bare = dep.split("::", 1)[1] if "::" in dep else dep
            pairs.append(f"{bare}={self._dotted_or_stem(bare)}")
        return ", ".join(pairs)

    def _snake_fallback(self, class_name: str) -> str:
        """Fallback snake_case conversion when no toolkit is available."""
        if not class_name:
            return ""
        out: list[str] = []
        for idx, ch in enumerate(class_name):
            if ch.isupper() and idx > 0:
                prev = class_name[idx - 1]
                if prev.islower() or prev.isdigit():
                    out.append("_")
                elif idx + 1 < len(class_name) and class_name[idx + 1].islower():
                    out.append("_")
            out.append(ch.lower())
        return "".join(out)
