"""Tests for TargetLanguage enum."""

from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def test_target_language_has_python() -> None:
    assert TargetLanguage.PYTHON.value == "python"


def test_target_language_has_javascript() -> None:
    assert TargetLanguage.JAVASCRIPT.value == "javascript"


def test_target_language_has_typescript() -> None:
    assert TargetLanguage.TYPESCRIPT.value == "typescript"


def test_target_language_has_java() -> None:
    assert TargetLanguage.JAVA.value == "java"


def test_target_language_membership() -> None:
    members = {m.name for m in TargetLanguage}
    assert members == {"PYTHON", "JAVASCRIPT", "TYPESCRIPT", "JAVA", "GO", "RUST"}


def test_target_language_has_go() -> None:
    assert TargetLanguage.GO.value == "go"


def test_target_language_has_rust() -> None:
    assert TargetLanguage.RUST.value == "rust"
