"""Tests for the SecurityReviewContext DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _module() -> ModuleSpec:
    cls = ClassSpec(
        name="Foo", pattern="SimpleClass", implements=None,
        methods=("bar()",), depends=(), concretes=(),
    )
    return ModuleSpec(
        name="M", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="P0", tier=0, slug="calc", description="A calculator",
        required_bounded_contexts=[], acceptance_criteria=["add works"],
        expected_module_count=(1, 1), expected_class_count=(1, 3),
        required_patterns=["ValueObject"], target_language=TargetLanguage.PYTHON,
    )


def test_security_review_context_is_frozen() -> None:
    ctx = SecurityReviewContext(module=_module(), problem=_problem())
    assert ctx.module.name == "M"
    with pytest.raises(FrozenInstanceError):
        setattr(ctx, "module", _module())  # noqa: B010
