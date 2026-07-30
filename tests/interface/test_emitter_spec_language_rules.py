"""Drift guards for the R0.11 emitter-spec language rules.

P2JAVA failed on `float`/`double` narrowing and P2TS on mutation of a
`readonly` ValueObject field. The fixes live in emitter spec TEXT, which
nothing else executes — so these guards parse the specs and fail if the
rules drift out (same approach as the R0.1 pattern-catalog guard).
"""

from pathlib import Path

import pytest

_EMITTERS = (
    Path(__file__).resolve().parents[2]
    / "squeaky_clean" / "interface" / "agent_specs" / "emitters"
)

_JAVA_BEHAVIORAL = sorted(
    p.name for p in (_EMITTERS / "java" / "behavioral").glob("*.md")
)


@pytest.mark.parametrize("spec_name", _JAVA_BEHAVIORAL)
def test_java_behavioral_specs_map_float_to_double(spec_name: str) -> None:
    text = (_EMITTERS / "java" / "behavioral" / spec_name).read_text()
    assert "`float` → `double`" in text or "`float` -> `double`" in text, (
        f"{spec_name}: missing §Notation float→double fidelity rule "
        "(P2JAVA lossy-conversion regression, R0.11)"
    )


@pytest.mark.parametrize("spec_name", ["EntityEmitter.md", "AggregateEmitter.md"])
def test_ts_specs_forbid_mutating_valueobject_siblings(spec_name: str) -> None:
    text = (_EMITTERS / "typescript" / "ddd_clean" / spec_name).read_text()
    assert "TS2540" in text, (
        f"{spec_name}: missing readonly-ValueObject mutation rule "
        "(P2TS TS2540 regression, R0.11)"
    )


@pytest.mark.parametrize("lang", ["java", "typescript"])
def test_strategy_specs_key_interface_emission_on_concretes(lang: str) -> None:
    """The abstract-participant contract PolymorphicRoleNormalizer feeds."""
    text = (_EMITTERS / lang / "behavioral" / "StrategyEmitter.md").read_text()
    assert "concretes" in text and "implements" in text, (
        f"{lang}/StrategyEmitter.md no longer keys the abstract/concrete "
        "role on `concretes`/`implements` — PolymorphicRoleNormalizer "
        "depends on that contract (R0.11)"
    )
