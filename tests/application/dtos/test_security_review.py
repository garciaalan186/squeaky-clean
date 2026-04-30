"""Tests for the SecurityReview DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.dtos.security_review import SecurityReview


def test_security_review_is_frozen() -> None:
    review = SecurityReview(concerns=())
    assert review.concerns == ()
    with pytest.raises(FrozenInstanceError):
        setattr(review, "concerns", ())  # noqa: B010


def test_security_review_with_concerns() -> None:
    c = SecurityConcern(
        category="injection",
        target_class="Calculator",
        description="SQL injection risk",
        test_scenario="Pass SQL payload as input",
    )
    review = SecurityReview(concerns=(c,))
    assert len(review.concerns) == 1
    assert review.concerns[0].category == "injection"
