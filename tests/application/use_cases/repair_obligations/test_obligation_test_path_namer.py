"""Tests for ObligationTestPathNamer (per-language test-file naming)."""

from squeaky_clean.application.generation.repair.obligations.obligation_test_path_namer import (
    ObligationTestPathNamer,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_NAMER = ObligationTestPathNamer()


def test_python_paths() -> None:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    assert _NAMER.canonical("OrderService", tk) == "tests/test_order_service.py"
    assert _NAMER.invariants_path("OrderService", tk) == (
        "tests/test_order_service_invariants.py"
    )


def test_typescript_and_javascript_paths() -> None:
    ts = LanguageToolkitFactory().for_language(TargetLanguage.TYPESCRIPT)
    js = LanguageToolkitFactory().for_language(TargetLanguage.JAVASCRIPT)
    assert _NAMER.canonical("OrderService", ts) == "tests/orderService.test.ts"
    assert _NAMER.canonical("OrderService", js) == "tests/orderService.test.js"
    assert _NAMER.invariants_path("OrderService", ts) == (
        "tests/orderServiceInvariants.test.ts"
    )


def test_java_paths() -> None:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    assert _NAMER.canonical("OrderService", tk) == (
        "src/test/java/com/example/OrderServiceTest.java"
    )
    assert _NAMER.invariants_path("OrderService", tk) == (
        "src/test/java/com/example/OrderServiceInvariantsTest.java"
    )


def test_none_toolkit_yields_none() -> None:
    assert _NAMER.canonical("X", None) is None
    assert _NAMER.invariants_path("X", None) is None


def test_forms_cover_snake_and_camel() -> None:
    assert _NAMER.forms("OrderService") == {
        "OrderService", "order_service", "orderService",
    }
