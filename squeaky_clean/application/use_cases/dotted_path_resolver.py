"""DottedPathResolver: convert (layer, module, class) into a Python dotted path."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class DottedPathResolver:
    """Resolves a sibling/dependency class to its layered Python dotted path.

    Returns ``src.<layer>.<module>.<snake_class>`` when the toolkit uses
    snake_case identifiers (Python). Otherwise falls back to the bare
    snake stem so non-Python languages keep their flat layout.
    """

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._camel: PascalToCamelConverter = PascalToCamelConverter()

    def resolve(
        self,
        class_name: str,
        module: ModuleSpec,
        architecture: ArchitectureSpec | None = None,
    ) -> str:
        """Return the dotted module path for ``class_name``.

        First searches the focal ``module`` for the class, then any
        ``architecture`` sibling module. Falls back to the focal module
        if not found anywhere.
        """
        owner = self._find_owner(class_name, module, architecture)
        # camelCase languages (TS/JS/Go) name files camelCase in
        # AssignPatternsPaths._stem; the import stem handed to ICPs must
        # match, or generated `import ... from './<stem>.js'` won't resolve.
        if self._toolkit.identifier_case == "camel":
            return self._camel.convert(class_name)
        stem = self._snake.convert(class_name)
        if self._toolkit.identifier_case != "snake":
            return stem
        layer = owner.layer.value.lower()
        mod_slug = self._snake.convert(owner.name)
        return f"src.{layer}.{mod_slug}.{stem}"

    def _find_owner(
        self,
        class_name: str,
        module: ModuleSpec,
        architecture: ArchitectureSpec | None,
    ) -> ModuleSpec:
        if any(c.name == class_name for c in module.classes):
            return module
        if architecture is None:
            return module
        for sibling in architecture.modules:
            if any(c.name == class_name for c in sibling.classes):
                return sibling
        return module
