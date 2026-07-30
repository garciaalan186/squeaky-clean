"""Golden-Squib routing test: a hand-authored Squib demanding pattern X must
route its focal class to X's dedicated ICP — never the SimpleClass escape hatch.

Each fixture in eval/squib_fixtures/ is a minimal §Notation an architect could
emit. This exercises the full parse -> AssignPatterns path (what the pipeline
uses), across every supported language, for the 28 patterns that no benchmark
ProblemSpec currently requires. It is deterministic (no LLM calls).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import squeaky_clean
from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_FIXTURES = Path(__file__).resolve().parents[2] / "eval" / "squib_fixtures"
_ICPS_ROOT = (
    Path(squeaky_clean.__file__).parent / "interface" / "agent_specs" / "emitters"
)
_MANIFEST: dict[str, dict[str, str]] = json.loads(
    (_FIXTURES / "manifest.json").read_text()
)
_CASES = [
    (pattern, info, language)
    for pattern, info in sorted(_MANIFEST.items())
    for language in TargetLanguage
]


def _idfn(val: object) -> str:
    if isinstance(val, TargetLanguage):
        return val.value
    if isinstance(val, dict):
        return ""
    return str(val)


@pytest.mark.parametrize(("pattern", "info", "language"), _CASES, ids=_idfn)
def test_golden_squib_routes_focal_class_to_dedicated_icp(
    pattern: str, info: dict[str, str], language: TargetLanguage,
) -> None:
    toolkit = LanguageToolkitFactory().for_language(language)
    arch = ParseArchitectureNotation().parse(
        (_FIXTURES / info["file"]).read_text()
    )
    assignments = AssignPatterns(toolkit, Path("/tmp/golden")).assign_all(
        arch.modules[0]
    )
    focal = next(a for a in assignments if a.class_spec.name == info["focal"])

    expected = f"{toolkit.icp_library}/{info['category']}/{pattern}Emitter"
    assert focal.emitter_spec_name == expected, (
        f"{pattern} focal class {info['focal']} ({language.value}) routed to "
        f"{focal.emitter_spec_name}, expected {expected}"
    )
    assert not focal.emitter_spec_name.endswith("SimpleClassEmitter"), (
        f"{pattern} ({language.value}) degraded to the SimpleClass escape hatch"
    )
    assert (_ICPS_ROOT / f"{focal.emitter_spec_name}.md").is_file(), (
        f"routed spec {focal.emitter_spec_name} has no file on disk"
    )


def test_fixtures_cover_every_benchmark_uncovered_pattern() -> None:
    # The 6 patterns some ProblemSpec already requires are exempt; every other
    # catalog pattern must have a golden-Squib fixture.
    from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS

    covered_by_benchmarks = {
        "Entity", "ValueObject", "SimpleClass", "UseCase", "Repository", "Strategy",
    }
    expected = set(ALL_PATTERNS) - covered_by_benchmarks
    assert set(_MANIFEST) == expected, (
        f"fixture/pattern drift: missing={expected - set(_MANIFEST)}, "
        f"extra={set(_MANIFEST) - expected}"
    )
