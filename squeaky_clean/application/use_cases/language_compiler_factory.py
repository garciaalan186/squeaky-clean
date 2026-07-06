"""language_compiler_factory: pick a ProjectCompiler adapter for a language."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.java_compiler import JavaCompiler
from squeaky_clean.infrastructure.compilation.typescript_compiler import (
    TypeScriptCompiler,
)


class LanguageCompilerFactory:
    """Returns the ProjectCompiler for a TargetLanguage, or None.

    Only languages with a meaningful ahead-of-time compile/typecheck step
    have an adapter (TypeScript via tsc, Java via mvn). Dynamically-typed
    or not-yet-supported languages return None, so the pipeline's compile
    gate is skipped for them.
    """

    def for_language(self, lang: TargetLanguage) -> ProjectCompiler | None:
        """Return the compiler for ``lang``, or None when there is none."""
        if lang is TargetLanguage.TYPESCRIPT:
            return TypeScriptCompiler()
        if lang is TargetLanguage.JAVA:
            return JavaCompiler()
        return None
