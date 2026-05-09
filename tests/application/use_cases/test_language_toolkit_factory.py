"""Tests for LanguageToolkitFactory."""

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def test_factory_returns_python_toolkit() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    assert toolkit.language is TargetLanguage.PYTHON
    assert toolkit.file_extension == ".py"
    assert toolkit.test_file_prefix == "test_"
    assert toolkit.test_file_suffix == ".py"
    assert toolkit.icp_library == "python"
    assert toolkit.architect_library == "python"
    assert toolkit.identifier_case == "snake"


def test_factory_returns_javascript_toolkit() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVASCRIPT)
    assert toolkit.language is TargetLanguage.JAVASCRIPT
    assert toolkit.file_extension == ".js"
    assert toolkit.test_file_prefix == ""
    assert toolkit.test_file_suffix == ".test.js"
    assert toolkit.icp_library == "javascript"
    assert toolkit.architect_library == "javascript"
    assert toolkit.identifier_case == "camel"


def test_factory_returns_java_toolkit() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    assert toolkit.language is TargetLanguage.JAVA
    assert toolkit.file_extension == ".java"
    assert toolkit.test_file_prefix == ""
    assert toolkit.test_file_suffix == "Test.java"
    assert toolkit.icp_library == "java"
    assert toolkit.architect_library == "java"
    assert toolkit.identifier_case == "pascal"
    assert toolkit.source_subdir == "src/main/java"
    assert toolkit.test_subdir == "src/test/java"


def test_factory_returns_go_toolkit() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.GO)
    assert toolkit.language is TargetLanguage.GO
    assert toolkit.file_extension == ".go"
    assert toolkit.test_file_prefix == ""
    assert toolkit.test_file_suffix == "_test.go"
    assert toolkit.icp_library == "go"
    assert toolkit.architect_library == "go"
    assert toolkit.identifier_case == "camel"
    assert toolkit.error_types_tuple == "error"
    assert toolkit.array_type_template == "[]{T}"


def test_factory_returns_rust_toolkit() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.RUST)
    assert toolkit.language is TargetLanguage.RUST
    assert toolkit.file_extension == ".rs"
    assert toolkit.test_file_prefix == ""
    assert toolkit.test_file_suffix == ".rs"
    assert toolkit.icp_library == "rust"
    assert toolkit.architect_library == "rust"
    assert toolkit.identifier_case == "snake"
    assert toolkit.array_type_template == "Vec<{T}>"
    assert "assert_eq!" in toolkit.assert_eq_template
