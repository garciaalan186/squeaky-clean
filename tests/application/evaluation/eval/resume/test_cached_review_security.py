"""Tests for CachedReviewSecurity (cached stand-in, no LLM call)."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.cached_review_security import (
    CachedReviewSecurity,
)
from squeaky_clean.application.generation.security.security_review import SecurityReview
from squeaky_clean.application.generation.security.security_review_context import (
    SecurityReviewContext,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def test_cached_review_security_returns_injected_review() -> None:
    review = SecurityReview(concerns=())
    stub = CachedReviewSecurity(review)
    module = ModuleSpec(name="Auth", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    ctx = SecurityReviewContext(module=module, problem=P0)
    assert stub.execute(ctx) is review
