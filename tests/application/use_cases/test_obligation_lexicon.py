"""Tests for obligation_lexicon (extracted from ProjectTestObligations)."""

from squeaky_clean.application.generation.testgen.obligation_lexicon import (
    is_validation_invariant,
    normalize,
    then_outcome,
    when_verb,
)
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind


def test_normalize_strips_underscores_and_case() -> None:
    assert normalize("Archive_Event") == "archiveevent"


def test_when_verb_extracts_first_identifier_after_when() -> None:
    assert when_verb("Given X, When archive_event is called, Then Y") \
        == "archive_event"
    assert when_verb("no clause here") is None


def test_then_outcome_classifies_raises_equals_field_call() -> None:
    assert then_outcome("Then an error is raised") == (AssertionKind.RAISES, "")
    assert then_outcome("Then result is 42") == (AssertionKind.EQUALS, "42")
    assert then_outcome("Then the payload holds data") \
        == (AssertionKind.FIELD_HOLDS, "")
    assert then_outcome("Then something happens") \
        == (AssertionKind.CALL_ONLY, "")


def test_validation_invariant_requires_value_constraint() -> None:
    assert is_validation_invariant("amount must be positive")
    assert not is_validation_invariant("events publish to the audit topic")
    # Behavioural keyword wins even when a validation keyword is present.
    assert not is_validation_invariant("field names must be valid verbatim")
