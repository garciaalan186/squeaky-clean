"""Tests for LanguageTestRunnerFactory."""

import pytest

from squeaky_clean.domain.interfaces.test_runner import TestRunner
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY
from squeaky_clean.interface.cli.language_test_runner_factory import (
    LanguageTestRunnerFactory,
)


def test_python_resolves_to_pytest_runner() -> None:
    runner = LanguageTestRunnerFactory().for_language(TargetLanguage.PYTHON)
    assert isinstance(runner, PytestRunner)


def test_javascript_resolves_to_node_runner() -> None:
    runner = LanguageTestRunnerFactory().for_language(TargetLanguage.JAVASCRIPT)
    assert isinstance(runner, NodeTestRunner)


def test_every_target_language_yields_a_test_runner() -> None:
    factory = LanguageTestRunnerFactory()
    for lang in TargetLanguage:
        assert isinstance(factory.for_language(lang), TestRunner)


def test_unregistered_language_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(REGISTRY, TargetLanguage.GO)
    with pytest.raises(ValueError, match="unsupported TargetLanguage"):
        LanguageTestRunnerFactory().for_language(TargetLanguage.GO)
