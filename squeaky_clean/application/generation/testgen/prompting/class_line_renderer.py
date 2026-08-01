"""ClassLineRenderer: per-class prompt lines (focal + cross-module)."""

from squeaky_clean.application.generation.emission.dotted_class_path_resolver import (
    DottedClassPathResolver,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.language.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class ClassLineRenderer:
    """Renders ``  - <Class> [...]`` lines, with file= paths when layered."""

    def __init__(self, ctx: TestArchitectureContext) -> None:
        """Constructed per format() call: ``ctx`` fixes toolkit + layout."""
        self._ctx = ctx
        self._snake = SnakeCaseConverter()
        self._layered = (
            ctx.toolkit is not None
            and ctx.toolkit.identifier_case == "snake"
        )

    def class_line(self, cls: ClassSpec, module: ModuleSpec) -> str:
        """One inventory line for a class of the focal module."""
        fields = ", ".join(cls.fields) if cls.fields else ""
        methods = ", ".join(cls.methods) if cls.methods else ""
        prefix = (
            f"  - {cls.name} [{cls.pattern}] "
            f"fields=[{fields}] methods=[{methods}]"
        )
        if not self._layered:
            return prefix
        return f"{prefix} file={self._dotted(cls, module)}"

    def cross_module(self, focal: ModuleSpec, arch: ArchitectureSpec) -> list[str]:
        """Exported sibling classes the focal module may import."""
        out: list[str] = []
        for sibling in arch.modules:
            if sibling.name == focal.name:
                continue
            for cls in sibling.classes:
                if cls.name not in sibling.exports:
                    continue
                fields = ", ".join(cls.fields) if cls.fields else ""
                methods = ", ".join(cls.methods) if cls.methods else ""
                out.append(
                    f"  - {cls.name} [{cls.pattern}] "
                    f"fields=[{fields}] methods=[{methods}] "
                    f"file={self._dotted(cls, sibling)}"
                )
        return out

    def _dotted(self, cls: ClassSpec, module: ModuleSpec) -> str:
        if self._ctx.toolkit is not None:
            return DottedClassPathResolver(self._ctx.toolkit).resolve(cls, module)
        layer = module.layer.value.lower()
        mod_slug = self._snake.convert(module.name)
        stem = self._snake.convert(cls.name)
        return f"src.{layer}.{mod_slug}.{stem}"
