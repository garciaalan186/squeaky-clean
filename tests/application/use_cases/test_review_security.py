"""Tests for ReviewSecurity use case."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.review_security import ReviewSecurity
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_CANNED = """SECURITY_REVIEW
---
CONCERN boundary Calculator
DESCRIPTION Numeric overflow not handled
TEST Pass MAX_INT as operand and verify behavior
---
"""


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content: str = content
        self.last_request: LLMRequest | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(self._content, 10, 5, 0.001, 50)


def _module() -> ModuleSpec:
    cls = ClassSpec(
        name="Calculator", pattern="SimpleClass", implements=None,
        methods=("add(a: int, b: int): int",), depends=(), concretes=(),
    )
    return ModuleSpec(
        name="Calculator", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )


def test_execute_returns_parsed_security_review() -> None:
    gateway = _StubGateway(_CANNED)
    deps = LLMCallDeps(
        gateway=gateway, router=ModelRouter(), recorder=LLMUsageRecorder()
    )
    ctx = SecurityReviewContext(module=_module(), problem=P0)
    review = ReviewSecurity(deps).execute(ctx)
    assert len(review.concerns) == 1
    assert review.concerns[0].category == "boundary"
    assert gateway.last_request is not None
    assert "SecurityArchitect" in (gateway.last_request.system_prompt or "")


def test_execute_records_token_usage() -> None:
    gateway = _StubGateway(_CANNED)
    recorder = LLMUsageRecorder()
    deps = LLMCallDeps(gateway=gateway, router=ModelRouter(), recorder=recorder)
    ctx = SecurityReviewContext(module=_module(), problem=P0)
    ReviewSecurity(deps).execute(ctx)
    assert recorder.stats("security_architect")[:2] == (10, 5)
