"""Drift guard: the RequirementCompiler's allowed-pattern list (constraint #3)
must stay in sync with the framework's PatternName catalog.

A stale whitelist silently makes whole emitter families unreachable from the
greenfield path — the exact defect that caused P7 (State) and P9 (Visitor) to
be emitted as Strategy. This test fails the build if they ever diverge.
"""

from pathlib import Path

import squeaky_clean
from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS

_SPEC = (
    Path(squeaky_clean.__file__).parent
    / "interface" / "agent_specs" / "architects" / "RequirementCompiler.md"
)


def _catalog_in_spec() -> set[str]:
    text = _SPEC.read_text()
    line = next(
        ln for ln in text.splitlines()
        if "one pattern from this catalog" in ln
    )
    listed = line.split("selectable):", 1)[1].split(". Use these names", 1)[0]
    return {tok.strip().rstrip(".") for tok in listed.split(",") if tok.strip()}


def test_architect_catalog_matches_pattern_name_exactly() -> None:
    spec_patterns = _catalog_in_spec()
    catalog = set(ALL_PATTERNS)
    assert spec_patterns == catalog, (
        f"RequirementCompiler #3 out of sync with PatternName:\n"
        f"  missing from spec: {sorted(catalog - spec_patterns)}\n"
        f"  invalid in spec:   {sorted(spec_patterns - catalog)}"
    )


def test_architect_catalog_has_no_bare_factory() -> None:
    # 'Factory' is not a PatternName; it silently routes to SimpleClass.
    assert "Factory" not in _catalog_in_spec()
