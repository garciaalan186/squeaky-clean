"""Integration test: LanguageAdapterSelector returns correct parser per language."""

import pytest

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.parsers.go_implemented_class_parser import (
    GoImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.java_implemented_class_parser import (
    JavaImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.javascript_implemented_class_parser import (
    JavaScriptImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.rust_implemented_class_parser import (
    RustImplementedClassParser,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector


@pytest.mark.parametrize(
    "language,parser_cls",
    [
        (TargetLanguage.PYTHON, PythonImplementedClassParser),
        (TargetLanguage.JAVA, JavaImplementedClassParser),
        (TargetLanguage.GO, GoImplementedClassParser),
        (TargetLanguage.RUST, RustImplementedClassParser),
        (TargetLanguage.JAVASCRIPT, JavaScriptImplementedClassParser),
        (TargetLanguage.TYPESCRIPT, JavaScriptImplementedClassParser),
    ],
)
def test_selector_returns_matching_parser(
    language: TargetLanguage, parser_cls: type,
) -> None:
    toolkit = LanguageToolkitFactory().for_language(language)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.parser, parser_cls)
