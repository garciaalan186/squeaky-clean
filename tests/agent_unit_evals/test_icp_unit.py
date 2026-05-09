"""A1: ICP output scorer — frozen-fixture unit eval."""

from pathlib import Path

from squeaky_clean.eval.agent_scorers.icp_scorer import ICPScorer

_FIX = Path(__file__).parent / "fixtures" / "icp"


def test_good_calculator_simple_class_scores_full() -> None:
    raw = (_FIX / "calculator_simple_class.txt").read_text()
    score = ICPScorer().score("calc_good", raw, "Calculator")
    assert score.parsed is True
    assert score.structural_pass == 1.0


def test_missing_class_marker_flagged() -> None:
    raw = "```python\ndef foo() -> None:\n    pass\n```\n"
    score = ICPScorer().score("missing_class", raw, "Calculator")
    assert score.structural_pass == 0.0


def test_todo_placeholder_flagged() -> None:
    raw = (
        "```python\nclass Calculator:\n    def add(self) -> int:\n"
        "        return 0  # TODO\n```\n"
    )
    score = ICPScorer().score("with_todo", raw, "Calculator")
    assert any("TODO" in i for i in score.issues)
