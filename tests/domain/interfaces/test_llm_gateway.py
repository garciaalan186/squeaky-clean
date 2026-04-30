"""Tests for LLMGateway ABC."""

import pytest

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class _StubGateway(LLMGateway):
    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=f"echo:{request.user_prompt}",
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.0,
            duration_ms=0,
        )


def test_llm_gateway_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        LLMGateway()  # type: ignore[abstract]


def test_llm_gateway_subclass_complete_works() -> None:
    gw = _StubGateway()
    resp = gw.complete(LLMRequest(model="m", system_prompt="s", user_prompt="hi"))
    assert resp.content == "echo:hi"
