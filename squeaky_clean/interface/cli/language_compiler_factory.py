"""language_compiler_factory: compiler view over the LanguageAdapterRegistry (R6.7)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY


class LanguageCompilerFactory:
    """Returns the ProjectCompiler for a TargetLanguage, or None.

    Only languages with a meaningful ahead-of-time compile/typecheck step
    have an adapter (TypeScript via tsc, Java via mvn). Dynamically-typed
    or not-yet-supported languages return None, so the pipeline's compile
    gate is skipped for them.
    """

    def for_language(self, lang: TargetLanguage) -> ProjectCompiler | None:
        """Return the compiler for ``lang``, or None when there is none."""
        entry = REGISTRY.get(lang)
        if entry is None or entry.compiler is None:
            return None
        return entry.compiler()
