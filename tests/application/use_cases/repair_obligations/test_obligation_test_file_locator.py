"""Tests for ObligationTestFileLocator (gap -> test-file grouping)."""

from pathlib import Path

from squeaky_clean.application.generation.repair.obligations.obligation_repair_request import (
    ObligationRepairRequest,
)
from squeaky_clean.application.generation.repair.obligations.obligation_test_file_locator import (
    ObligationTestFileLocator,
)
from squeaky_clean.application.generation.testgen.test_obligation import TestObligation
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _request(
    tmp_path: Path, *obligations: TestObligation,
    language: TargetLanguage = TargetLanguage.PYTHON,
) -> ObligationRepairRequest:
    tk = LanguageToolkitFactory().for_language(language)
    return ObligationRepairRequest(tuple(obligations), tmp_path, tk, 1)


def _ob(method: str = "ingest") -> TestObligation:
    return TestObligation("Ingester", method, AssertionKind.RAISES,
                          "on bad input", "AC1")


def test_prefers_the_test_file_whose_stem_is_the_class(tmp_path: Path) -> None:
    java_tests = tmp_path / "src" / "test" / "java" / "com" / "example"
    java_tests.mkdir(parents=True)
    (java_tests / "IngesterTest.java").write_text("class IngesterTest {}\n")
    (java_tests / "OtherTest.java").write_text("// uses Ingester\n")
    request = _request(tmp_path, _ob(), language=TargetLanguage.JAVA)
    groups = ObligationTestFileLocator().group(request.obligations, request)
    assert list(groups) == ["src/test/java/com/example/IngesterTest.java"]


def test_falls_back_to_a_file_mentioning_the_class(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_other.py").write_text("from x import Ingester\n")
    request = _request(tmp_path, _ob())
    groups = ObligationTestFileLocator().group(request.obligations, request)
    assert list(groups) == ["tests/test_other.py"]


def test_missing_test_file_gets_a_canonical_new_path(tmp_path: Path) -> None:
    request = _request(tmp_path, _ob())
    groups = ObligationTestFileLocator().group(request.obligations, request)
    assert list(groups) == ["tests/test_ingester.py"]


def test_constructor_duties_route_to_a_fresh_invariants_file(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path, _ob(method="<init>"))
    groups = ObligationTestFileLocator().group(request.obligations, request)
    assert list(groups) == ["tests/test_ingester_invariants.py"]
