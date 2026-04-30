"""Tests for ParseSecurityReview."""

from squeaky_clean.application.use_cases.parse_security_review import ParseSecurityReview

_SAMPLE = """SECURITY_REVIEW
---
CONCERN input_validation Calculator
DESCRIPTION Empty string input not handled by compute method
TEST Pass empty string as operator and expect ValueError

CONCERN boundary Operand
DESCRIPTION Negative values not validated in constructor
TEST Pass -1 as operand value and verify error is raised

CONCERN error_handling Calculator
DESCRIPTION Error messages may leak internal class structure
TEST Trigger error and verify message has no file paths
---
"""


def test_parse_extracts_all_concerns() -> None:
    review = ParseSecurityReview().parse(_SAMPLE)
    assert len(review.concerns) == 3
    assert review.concerns[0].category == "input_validation"
    assert review.concerns[0].target_class == "Calculator"
    assert "Empty string" in review.concerns[0].description
    assert "ValueError" in review.concerns[0].test_scenario


def test_parse_boundary_concern() -> None:
    review = ParseSecurityReview().parse(_SAMPLE)
    c = review.concerns[1]
    assert c.category == "boundary"
    assert c.target_class == "Operand"
    assert "Negative" in c.description


def test_parse_empty_returns_empty_review() -> None:
    review = ParseSecurityReview().parse("no valid section here")
    assert len(review.concerns) == 0


def test_parse_tolerant_of_whitespace() -> None:
    raw = "\n\n  " + _SAMPLE + "\n\n"
    review = ParseSecurityReview().parse(raw)
    assert len(review.concerns) == 3
