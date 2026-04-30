"""Unit tests for ComposeAgentSpec."""

from squeaky_clean.application.use_cases.compose_agent_spec import ComposeAgentSpec
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class _FakeLoader(LoadAgentSpec):
    def __init__(self, text: str) -> None:
        self._text = text

    def load(self, name: str) -> str:
        return self._text


def test_substitutes_known_placeholders() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    template = (
        "Use {{file_extension}} files. Errors: {{error_types_tuple}}.\n"
        "Imports: {{test_framework_imports}}"
    )
    out = ComposeAgentSpec(_FakeLoader(template)).compose("X", toolkit)
    assert ".py" in out
    assert "ValueError, ZeroDivisionError" in out
    assert "import pytest" in out


def test_unknown_placeholder_left_literal() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    out = ComposeAgentSpec(_FakeLoader("{{not_a_real_field}}")).compose("X", toolkit)
    assert out == "{{not_a_real_field}}"


def test_language_placeholder_swaps_per_language() -> None:
    template = "lang={{language}}"
    p = ComposeAgentSpec(_FakeLoader(template)).compose(
        "X", LanguageToolkitFactory().for_language(TargetLanguage.PYTHON),
    )
    j = ComposeAgentSpec(_FakeLoader(template)).compose(
        "X", LanguageToolkitFactory().for_language(TargetLanguage.JAVA),
    )
    assert "python" in p
    assert "java" in j
