"""A1: TestArchitect output scorer — frozen-fixture unit eval."""

from pathlib import Path

from squeaky_clean.application.use_cases.parse_notation import ParseNotation
from squeaky_clean.eval.agent_scorers.test_architect_scorer import TestArchitectScorer

_FIX_TA = Path(__file__).parent / "fixtures" / "test_architect"
_FIX_PA = Path(__file__).parent / "fixtures" / "principal_architect"


def test_good_test_architecture_scores_full() -> None:
    notation = (_FIX_PA / "p0_calculator_good.notation").read_text()
    module = ParseNotation().parse(notation)
    raw = (_FIX_TA / "p0_calculator_good.txt").read_text()
    score = TestArchitectScorer().score("p0_good", raw, module)
    assert score.parsed is True
    assert score.structural_pass == 1.0


def test_unparseable_test_architecture_returns_parse_error() -> None:
    notation = (_FIX_PA / "p0_calculator_good.notation").read_text()
    module = ParseNotation().parse(notation)
    score = TestArchitectScorer().score("garbage", "no headers here", module)
    assert score.parsed is False
    assert score.structural_pass == 0.0


def test_class_outside_modulespec_flagged() -> None:
    notation = (_FIX_PA / "p0_calculator_good.notation").read_text()
    module = ParseNotation().parse(notation)
    raw = """GHERKIN
---
Feature: Calculator
  Scenario: foo
    Given x
    When y
    Then z
---

TEST_SKELETONS
---
FILE tests/test_unknown.py
CLASS UnknownClass
```python
def test_unknown() -> None:
    pass
```
---
"""
    score = TestArchitectScorer().score("bad", raw, module)
    assert score.parsed is True
    assert any("UnknownClass" in i for i in score.issues)
