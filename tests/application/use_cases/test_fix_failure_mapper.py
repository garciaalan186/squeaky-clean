"""Tests for FixFailureMapper."""

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.fix_failure_mapper import FixFailureMapper
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _cls(name: str, path: str) -> ImplementedClass:
    return ImplementedClass(
        class_name=name, file_path=path, code="...",
        test_code=None, cost_usd=0.0, duration_ms=0,
        input_tokens=0, output_tokens=0,
    )


def test_python_matches_test_prefix_stem() -> None:
    classes = (_cls("Operand", "src/operand.py"),)
    mapper = FixFailureMapper(TargetLanguage.PYTHON)
    assert mapper.map(("test_operand",), classes) == classes


def test_python_matches_source_stem_too() -> None:
    classes = (_cls("Operand", "src/operand.py"),)
    mapper = FixFailureMapper(TargetLanguage.PYTHON)
    assert mapper.map(("operand",), classes) == classes


def test_javascript_matches_on_source_stem() -> None:
    classes = (_cls("Operand", "src/operand.js"),)
    mapper = FixFailureMapper(TargetLanguage.JAVASCRIPT)
    assert mapper.map(("operand",), classes) == classes


def test_java_matches_on_test_class_name() -> None:
    classes = (_cls("Operand", "src/main/java/Operand.java"),)
    mapper = FixFailureMapper(TargetLanguage.JAVA)
    assert mapper.map(("OperandTest",), classes) == classes


def test_no_match_returns_empty() -> None:
    classes = (_cls("Operand", "src/operand.py"),)
    assert FixFailureMapper(TargetLanguage.PYTHON).map(
        ("test_unrelated",), classes,
    ) == ()


def test_duplicate_stems_produce_single_class() -> None:
    classes = (_cls("Operand", "src/operand.py"),)
    assert FixFailureMapper(TargetLanguage.PYTHON).map(
        ("test_operand", "operand"), classes,
    ) == classes
