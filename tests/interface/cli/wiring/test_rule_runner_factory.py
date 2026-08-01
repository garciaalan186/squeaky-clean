"""Tests for RuleRunnerFactory (per-language architectural rule set)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.rules.dependency_rule import DependencyRule
from squeaky_clean.domain.rules.pattern_conformance import PatternConformanceRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.wiring.emission_wiring import EmissionWiring
from squeaky_clean.interface.cli.wiring.rule_runner_factory import RuleRunnerFactory
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


def _adapters_for(
    language: TargetLanguage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> tuple[object, object]:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    ctx = WiringContext.create(ModelRouter(), RunConfig())
    problem = ProblemSpec(
        id="P0", tier=0, slug="calc", description="x",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=language,
    )
    bundle = EmissionWiring(ctx).wire(problem)
    return bundle.adapters, bundle.toolkit


def test_python_gets_dependency_and_pattern_rules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapters, toolkit = _adapters_for(TargetLanguage.PYTHON, tmp_path, monkeypatch)
    runner = RuleRunnerFactory().build(adapters, toolkit)  # type: ignore[arg-type]
    rule_types = {type(r) for r in runner._rules}
    assert DependencyRule in rule_types
    assert PatternConformanceRule in rule_types


def test_non_python_gets_only_the_granularity_rule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapters, toolkit = _adapters_for(
        TargetLanguage.JAVASCRIPT, tmp_path, monkeypatch,
    )
    runner = RuleRunnerFactory().build(adapters, toolkit)  # type: ignore[arg-type]
    assert len(runner._rules) == 1


def test_toolkit_factory_reports_language() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    assert toolkit.language is TargetLanguage.PYTHON
