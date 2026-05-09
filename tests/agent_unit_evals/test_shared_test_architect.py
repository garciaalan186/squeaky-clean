"""B1: shared TestArchitect.md composes correctly for every supported language."""

from squeaky_clean.application.use_cases.compose_agent_spec import ComposeAgentSpec
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _compose_shared(lang: TargetLanguage) -> str:
    toolkit = LanguageToolkitFactory().for_language(lang)
    return ComposeAgentSpec().compose("_shared/TestArchitect", toolkit)


def test_python_composition_has_no_unfilled_placeholders() -> None:
    out = _compose_shared(TargetLanguage.PYTHON)
    assert "{{file_extension}}" not in out
    assert "{{language}}" not in out
    assert "{{error_types_tuple}}" not in out


def test_javascript_composition_has_node_test_imports() -> None:
    out = _compose_shared(TargetLanguage.JAVASCRIPT)
    assert "node:test" in out
    assert ".test.js" in out


def test_java_composition_has_junit_imports() -> None:
    out = _compose_shared(TargetLanguage.JAVA)
    assert "org.junit.jupiter" in out
    assert "Test.java" in out


def test_typescript_composition_has_ts_extension() -> None:
    out = _compose_shared(TargetLanguage.TYPESCRIPT)
    assert ".test.ts" in out


def test_invariant_default_rule_present_for_all_languages() -> None:
    for lang in TargetLanguage:
        out = _compose_shared(lang)
        assert "INVARIANT-SATISFYING" in out, f"missing in {lang.value}"
        assert "non-empty" in out
