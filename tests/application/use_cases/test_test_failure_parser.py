"""Tests for TestFailureParser."""

from squeaky_clean.application.use_cases.test_failure_parser import TestFailureParser
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def test_pytest_failed_lines_extract_source_stems() -> None:
    out = (
        "FAILED tests/test_operand.py::test_value_positive\n"
        "FAILED tests/test_calculator.py::test_add\n"
        "2 failed, 5 passed\n"
    )
    stems = TestFailureParser().parse(out, TargetLanguage.PYTHON)
    assert stems == ("test_calculator", "test_operand")


def test_pytest_error_lines_also_extracted() -> None:
    out = "ERROR tests/test_operand.py\n1 error\n"
    assert TestFailureParser().parse(out, TargetLanguage.PYTHON) == (
        "test_operand",
    )


def test_pytest_clean_output_returns_empty() -> None:
    assert TestFailureParser().parse(
        "5 passed in 0.1s", TargetLanguage.PYTHON,
    ) == ()


def test_node_location_lines_extract_stems() -> None:
    out = (
        "not ok 1 - something\n"
        "  location: 'tests/operand.test.js:5:1'\n"
        "  failureType: testCodeFailure\n"
    )
    assert TestFailureParser().parse(out, TargetLanguage.JAVASCRIPT) == (
        "operand",
    )


def test_typescript_dist_paths_extract_source_stem() -> None:
    out = "  location: 'dist/tests/operand.test.js:10:5'\n"
    assert TestFailureParser().parse(out, TargetLanguage.TYPESCRIPT) == (
        "operand",
    )


def test_maven_error_lines_extract_test_class() -> None:
    out = "[ERROR]   OperandTest.testAdd:15 AssertionError\n"
    assert TestFailureParser().parse(out, TargetLanguage.JAVA) == (
        "OperandTest",
    )


def test_maven_failure_in_class_extracted() -> None:
    out = "Tests run: 1, Failures: 1, Errors: 0 FAILURE! -- in com.example.CalculatorTest\n"
    assert TestFailureParser().parse(out, TargetLanguage.JAVA) == (
        "CalculatorTest",
    )


def test_maven_compile_error_extracts_source_stem() -> None:
    out = (
        "[ERROR] /full/path/src/main/java/ChatService.java:[49,27] "
        "incompatible types\n"
    )
    assert TestFailureParser().parse(out, TargetLanguage.JAVA) == (
        "ChatService",
    )


def test_typescript_tsc_error_extracts_source_stem() -> None:
    out = (
        "src/listPendingUseCase.ts(2,26): error TS2459: "
        "Module declares 'Todo' locally\n"
    )
    assert TestFailureParser().parse(out, TargetLanguage.TYPESCRIPT) == (
        "listPendingUseCase",
    )


def test_typescript_test_file_compile_error_extracted() -> None:
    out = "tests/operand.test.ts(5,10): error TS2304: Cannot find name 'Foo'\n"
    assert TestFailureParser().parse(out, TargetLanguage.TYPESCRIPT) == (
        "operand",
    )
