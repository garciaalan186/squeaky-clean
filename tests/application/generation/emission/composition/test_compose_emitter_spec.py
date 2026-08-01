"""Tests for ComposeEmitterSpec template-vs-fallback resolution."""

import re
from pathlib import Path

import pytest

from squeaky_clean.application.generation.emission.composition.compose_emitter_spec import (
    ComposeEmitterSpec,
)
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_ACTIVE = (
    TargetLanguage.PYTHON, TargetLanguage.JAVASCRIPT,
    TargetLanguage.TYPESCRIPT, TargetLanguage.JAVA,
)


def _toolkit(language: TargetLanguage) -> LanguageToolkit:
    return LanguageToolkitFactory().for_language(language)


@pytest.mark.parametrize("language", _ACTIVE)
def test_cut_over_pattern_composes_without_residue(
    language: TargetLanguage,
) -> None:
    toolkit = _toolkit(language)
    spec = ComposeEmitterSpec(LoadAgentSpec()).load(
        f"{toolkit.icp_library}/behavioral/StrategyEmitter", toolkit,
    )
    assert spec.startswith("# Role: StrategyEmitter")
    assert re.findall(r"\{\{[^}]+\}\}", spec) == [], "unresolved placeholders"
    assert f"```{toolkit.language.value}" in spec


@pytest.mark.parametrize("language", _ACTIVE)
def test_not_cut_over_pattern_falls_back_to_language_file(
    language: TargetLanguage,
) -> None:
    toolkit = _toolkit(language)
    name = f"{toolkit.icp_library}/ddd_clean/EntityEmitter"
    composed = ComposeEmitterSpec(LoadAgentSpec()).load(name, toolkit)
    assert composed == LoadAgentSpec().load(name)


def test_unqualified_names_pass_straight_through(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    (root / "architects").mkdir(parents=True)
    (root / "architects" / "Solo.md").write_text("# Role: Solo\n")
    loader = LoadAgentSpec(root)
    spec = ComposeEmitterSpec(loader).load("Solo", _toolkit(TargetLanguage.PYTHON))
    assert spec == "# Role: Solo\n"
