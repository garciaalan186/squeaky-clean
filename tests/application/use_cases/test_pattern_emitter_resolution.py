"""Resolution guardrail: every catalog PatternName resolves to a real ICP spec.

This is the invariant behind the marketing claim that one atomic agent
specializes in each of the 34 GoF/DDD patterns. If a pattern/language pair
has no dedicated spec on disk, this test fails instead of the router silently
degrading to SimpleClassEmitter at runtime.
"""

from pathlib import Path

import pytest

import squeaky_clean
from squeaky_clean.application.generation.emission.composition.compose_emitter_spec import (
    ComposeEmitterSpec,
)
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.emission.map_pattern_to_emitter import (
    ACTIVE_EMITTER_LANGUAGES,
    MapPatternToEmitter,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_ICPS_ROOT: Path = (
    Path(squeaky_clean.__file__).parent / "interface" / "agent_specs" / "emitters"
)
# R6.10: parametrize over ACTIVE_EMITTER_LANGUAGES, not the full enum —
# Go/Rust fleets are archived under agent_specs/_attic/emitters/ until a
# real problem funds them.
_CASES: list[tuple[str, TargetLanguage]] = [
    (pattern, language)
    for pattern in sorted(ALL_PATTERNS)
    for language in ACTIVE_EMITTER_LANGUAGES
]


@pytest.mark.parametrize(("pattern", "language"), _CASES)
def test_every_pattern_resolves_to_an_existing_spec(
    pattern: str, language: TargetLanguage,
) -> None:
    # R6.1a: a pattern is resolvable through EITHER its per-language spec
    # file OR the shared template + language profile — loaded through the
    # same ComposeEmitterSpec path production uses.
    toolkit = LanguageToolkitFactory().for_language(language)
    spec_name = MapPatternToEmitter().map(pattern, toolkit)
    try:
        text = ComposeEmitterSpec(LoadAgentSpec()).load(spec_name, toolkit)
    except FileNotFoundError:
        text = ""
    assert text.startswith("# Role:"), (
        f"{pattern} ({language.value}) resolved to {spec_name}, "
        f"but no per-language spec or shared template composes for it"
    )


@pytest.mark.parametrize(("pattern", "language"), _CASES)
def test_no_catalog_pattern_silently_degrades_to_simpleclass(
    pattern: str, language: TargetLanguage,
) -> None:
    spec_name = MapPatternToEmitter().map(
        pattern, LanguageToolkitFactory().for_language(language),
    )
    if pattern != "SimpleClass":
        assert not spec_name.endswith("SimpleClassEmitter"), (
            f"{pattern} ({language.value}) degraded to the SimpleClass "
            f"escape hatch instead of a dedicated ICP"
        )
