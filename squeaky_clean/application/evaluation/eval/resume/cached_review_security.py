"""CachedReviewSecurity: ReviewSecurity stand-in returning a cached review."""

from __future__ import annotations

from squeaky_clean.application.generation.security.security_review import SecurityReview
from squeaky_clean.application.generation.security.security_review_context import (
    SecurityReviewContext,
)


class CachedReviewSecurity:
    """Stand-in for ReviewSecurity that returns an empty SecurityReview."""

    def __init__(self, review: SecurityReview) -> None:
        self._review: SecurityReview = review

    def execute(self, context: SecurityReviewContext) -> SecurityReview:
        del context
        return self._review
