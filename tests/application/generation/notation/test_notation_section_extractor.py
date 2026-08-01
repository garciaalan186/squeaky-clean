"""Tests for NotationSectionExtractor top-level splitting."""

import pytest

from squeaky_clean.application.generation.notation.notation_section_extractor import (
    NotationSectionExtractor,
)
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError

_DOC = """MODULE Payment
LAYER Domain
EXPORTS [PaymentService]
CLASSES {
  Payment -> Entity {}
}
"""


def test_extracts_all_sections() -> None:
    sections = NotationSectionExtractor().extract(_DOC)
    assert sections["MODULE"] == "Payment"
    assert sections["LAYER"] == "Domain"
    assert sections["EXPORTS"] == "PaymentService"
    assert "Payment -> Entity" in sections["CLASSES"]


def test_duplicate_singleton_first_occurrence_wins() -> None:
    text = _DOC + "\nMODULE Second\nLAYER Application\nCLASSES {}\n"
    sections = NotationSectionExtractor().extract(text)
    assert sections["MODULE"] == "Payment"
    assert sections["LAYER"] == "Domain"


def test_duplicate_classes_bodies_are_merged() -> None:
    text = _DOC + "\nMODULE Second\nCLASSES {\n  Refund -> Entity {}\n}\n"
    sections = NotationSectionExtractor().extract(text)
    assert "Payment -> Entity" in sections["CLASSES"]
    assert "Refund -> Entity" in sections["CLASSES"]


def test_empty_input_raises() -> None:
    with pytest.raises(NotationParseError, match="empty"):
        NotationSectionExtractor().extract("   ")
