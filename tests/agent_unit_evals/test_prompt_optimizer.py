"""Unit tests for PromptOptimizer (offline; no live LLM)."""

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.eval.agent_scorers.prompt_candidate import PromptCandidate
from squeaky_clean.eval.agent_scorers.prompt_optimizer import (
    PromptOptimizer,
    make_fixture,
)


class _GoodGateway(LLMGateway):
    """Always emits a correct fenced class block."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="```python\nclass Calculator:\n    pass\n```\n",
            input_tokens=0, output_tokens=0, cost_usd=0.0, duration_ms=0,
        )


class _BadGateway(LLMGateway):
    """Emits prose, no fence."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="here is your class",
            input_tokens=0, output_tokens=0, cost_usd=0.0, duration_ms=0,
        )


def test_good_gateway_yields_full_score() -> None:
    opt = PromptOptimizer(_GoodGateway(), model="haiku")
    fx = [make_fixture("calc", "spec text", "Calculator")]
    cand = opt.evaluate("v1", "system prompt", fx)
    assert cand.mean_score == 1.0
    assert cand.fixtures_passed == 1


def test_bad_gateway_yields_zero_score() -> None:
    opt = PromptOptimizer(_BadGateway(), model="haiku")
    fx = [make_fixture("calc", "spec text", "Calculator")]
    cand = opt.evaluate("v1", "system prompt", fx)
    assert cand.mean_score == 0.0


def test_select_best_picks_max() -> None:
    a = PromptCandidate("a", "p", 0.3, 0, 3)
    b = PromptCandidate("b", "p", 0.9, 2, 3)
    c = PromptCandidate("c", "p", 0.6, 1, 3)
    opt = PromptOptimizer(_GoodGateway(), "haiku")
    assert opt.select_best([a, b, c]).name == "b"
