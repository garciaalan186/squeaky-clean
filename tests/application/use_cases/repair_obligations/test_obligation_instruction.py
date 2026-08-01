"""Tests for build_instruction (obligation repair prompt text)."""

from squeaky_clean.application.generation.repair.obligations.obligation_instruction import (
    build_instruction,
)
from squeaky_clean.application.generation.testgen.test_obligation import TestObligation
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind


def test_method_obligation_names_the_call_and_assertion() -> None:
    text = build_instruction([TestObligation(
        "Ingester", "ingest", AssertionKind.RAISES, "on bad input", "AC1",
    )])
    assert "call ingest on Ingester" in text
    assert "on bad input" in text
    assert "never a trivial one" in text


def test_constructor_obligation_demands_a_violating_construction() -> None:
    text = build_instruction([TestObligation(
        "Order", "<init>", AssertionKind.RAISES, "amount > 0", "AC2",
    )])
    assert "construct Order" in text
    assert 'VIOLATES "amount > 0"' in text
    assert "constructor raises" in text
