"""ClassPathsBlockRenderer: emit the `ClassPaths:` lines for the user prompt."""

from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.dotted_class_path_resolver import (
    DottedClassPathResolver,
)


class ClassPathsBlockRenderer:
    """Builds the lines of the ``ClassPaths:`` block for TestArchitect.

    Walks every class across the focal module and any sibling modules in
    the architecture, emitting one ``- ClassName: <dotted_path>`` per
    unique class name. Empty when no toolkit/classes are present.
    """

    def render(self, ctx: TestArchitectureContext) -> list[str]:
        """Return the indented ``ClassPaths:`` body lines (without header)."""
        if ctx.toolkit is None:
            return []
        modules = (
            ctx.architecture.modules if ctx.architecture is not None
            else (ctx.module,)
        )
        if not modules or not any(m.classes for m in modules):
            return []
        resolver = DottedClassPathResolver(ctx.toolkit)
        seen: set[str] = set()
        out: list[str] = []
        for mod in modules:
            for cls in mod.classes:
                if cls.name in seen:
                    continue
                seen.add(cls.name)
                out.append(f"  - {cls.name}: {resolver.resolve(cls, mod)}")
        return out
