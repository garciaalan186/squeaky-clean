"""Resolution guardrail: every catalog PatternName resolves to a real ICP spec.

This is the invariant behind the marketing claim that one atomic agent
specializes in each of the 34 GoF/DDD patterns. If a pattern/language pair
has no dedicated spec on disk, this test fails instead of the router silently
degrading to SimpleClassEmitter at runtime.
"""

from pathlib import Path

import pytest

import squeaky_clean
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.map_pattern_to_emitter import MapPatternToEmitter
from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_ICPS_ROOT: Path = (
    Path(squeaky_clean.__file__).parent / "interface" / "agent_specs" / "emitters"
)
_CASES: list[tuple[str, TargetLanguage]] = [
    (pattern, language)
    for pattern in sorted(ALL_PATTERNS)
    for language in TargetLanguage
]


@pytest.mark.parametrize(("pattern", "language"), _CASES)
def test_every_pattern_resolves_to_an_existing_spec(
    pattern: str, language: TargetLanguage,
) -> None:
    toolkit = LanguageToolkitFactory().for_language(language)
    spec_name = MapPatternToEmitter().map(pattern, toolkit)
    spec_file = _ICPS_ROOT / f"{spec_name}.md"
    assert spec_file.is_file(), (
        f"{pattern} ({language.value}) resolved to {spec_name}, "
        f"but {spec_file} does not exist"
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
