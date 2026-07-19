"""Tests for LanguageCompilerFactory language dispatch."""

from squeaky_clean.application.use_cases.language_compiler_factory import (
    LanguageCompilerFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.java_compiler import JavaCompiler
from squeaky_clean.infrastructure.compilation.typescript_compiler import (
    TypeScriptCompiler,
)


def test_typescript_gets_tsc_compiler() -> None:
    c = LanguageCompilerFactory().for_language(TargetLanguage.TYPESCRIPT)
    assert isinstance(c, TypeScriptCompiler)


def test_java_gets_maven_compiler() -> None:
    c = LanguageCompilerFactory().for_language(TargetLanguage.JAVA)
    assert isinstance(c, JavaCompiler)


def test_python_has_no_compiler() -> None:
    assert LanguageCompilerFactory().for_language(TargetLanguage.PYTHON) is None
