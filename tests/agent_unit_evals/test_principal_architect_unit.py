"""A1: PrincipalArchitect output scorer — frozen-fixture unit eval."""

from pathlib import Path

from squeaky_clean.eval.agent_scorers.principal_architect_scorer import (
    PrincipalArchitectScorer,
)

_FIXTURES = Path(__file__).parent / "fixtures" / "principal_architect"


def _load(name: str) -> str:
    return (_FIXTURES / name).read_text()


def test_good_p0_calculator_passes_structural_check() -> None:
    text = _load("p0_calculator_good.notation")
    score = PrincipalArchitectScorer().score("p0_calculator_good", text)
    assert score.parsed is True
    assert score.structural_pass == 1.0
    assert score.issues == ()


def test_undeclared_dep_fails_structural_check() -> None:
    text = _load("p0_calculator_bad_undeclared_dep.notation")
    score = PrincipalArchitectScorer().score("p0_calculator_bad", text)
    assert score.parsed is True
    assert score.structural_pass == 0.0
    assert any("Operand" in i for i in score.issues)
    assert any("Result" in i for i in score.issues)


def test_unparseable_input_returns_parse_error() -> None:
    score = PrincipalArchitectScorer().score("garbage", "not §Notation at all")
    assert score.parsed is False
    assert score.structural_pass == 0.0
    assert any("parse" in i for i in score.issues)
