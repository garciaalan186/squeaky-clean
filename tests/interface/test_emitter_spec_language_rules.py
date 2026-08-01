"""Drift guards for the R0.11 emitter-spec language rules.

P2JAVA failed on `float`/`double` narrowing and P2TS on mutation of a
`readonly` ValueObject field. The fixes live in emitter spec TEXT, which
nothing else executes — so these guards parse the specs and fail if the
rules drift out (same approach as the R0.1 pattern-catalog guard).
"""

from pathlib import Path

import pytest

from squeaky_clean.application.generation.emission.composition.compose_emitter_spec import (
    ComposeEmitterSpec,
)
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.emission.map_pattern_to_emitter import (
    MapPatternToEmitter,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_EMITTERS = (
    Path(__file__).resolve().parents[2]
    / "squeaky_clean" / "interface" / "agent_specs" / "emitters"
)

@pytest.mark.parametrize("pattern", ["Entity", "Aggregate"])
def test_ts_specs_forbid_mutating_valueobject_siblings(pattern: str) -> None:
    """R6.1a: the guard moved from 2 typescript file copies to the composed
    template output (the TS2540 rule lives in a {{#lang:typescript}} block)."""
    text = _composed(pattern, "typescript")
    assert "TS2540" in text, (
        f"composed typescript {pattern} spec lost the readonly-ValueObject "
        "mutation rule (P2TS TS2540 regression, R0.11)"
    )


def _composed(pattern: str, lang: str) -> str:
    """Compose a cut-over pattern's spec the way production does (R6.1a)."""
    language = TargetLanguage(lang)
    toolkit = LanguageToolkitFactory().for_language(language)
    spec_name = MapPatternToEmitter().map(pattern, toolkit)
    return ComposeEmitterSpec(LoadAgentSpec()).load(spec_name, toolkit)


@pytest.mark.parametrize("lang", ["java", "typescript"])
def test_strategy_specs_key_interface_emission_on_concretes(lang: str) -> None:
    """The abstract-participant contract PolymorphicRoleNormalizer feeds."""
    text = _composed("Strategy", lang)
    assert "concretes" in text and "implements" in text, (
        f"composed {lang} Strategy spec no longer keys the abstract/concrete "
        "role on `concretes`/`implements` — PolymorphicRoleNormalizer "
        "depends on that contract (R0.11)"
    )


_CUT_OVER_PATTERNS = sorted(
    p.stem.removesuffix("Emitter")
    for sub in ("behavioral", "structural", "creational", "ddd_clean")
    for p in (_EMITTERS / "_shared" / sub).glob("*Emitter.md")
) if (_EMITTERS / "_shared").is_dir() else []


@pytest.mark.parametrize("pattern", _CUT_OVER_PATTERNS)
def test_composed_java_specs_keep_float_to_double_rule(pattern: str) -> None:
    """R6.1a: the R0.11 drift guard moves from 4 file copies to ONE
    template+profile assertion for every cut-over pattern."""
    text = _composed(pattern, "java")
    assert "`float` → `double`" in text or "`float` -> `double`" in text, (
        f"composed java {pattern} spec lost the §Notation float→double "
        "fidelity rule (P2JAVA lossy-conversion regression, R0.11)"
    )
