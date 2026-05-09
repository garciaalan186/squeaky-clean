"""Tests for BudgetedGateway."""

import pytest

from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.use_cases.budgeted_gateway import BudgetedGateway
from squeaky_clean.application.use_cases.cost_gate import BudgetExceededError, CostGate
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class _CostStub(LLMGateway):
    def __init__(self, cost_usd: float) -> None:
        self._cost: float = cost_usd
        self.calls: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return LLMResponse(
            content="ok", input_tokens=1, output_tokens=1,
            cost_usd=self._cost, duration_ms=1,
        )


def _req() -> LLMRequest:
    return LLMRequest(model="m", system_prompt="s", user_prompt="u")


def test_records_each_call() -> None:
    gate = CostGate(CostBudget(max_cost_usd=10.0))
    g = BudgetedGateway(_CostStub(1.5), gate)
    g.complete(_req())
    g.complete(_req())
    assert gate.spent_usd() == 3.0


def test_raises_after_cap() -> None:
    gate = CostGate(CostBudget(max_cost_usd=2.0))
    inner = _CostStub(1.5)
    g = BudgetedGateway(inner, gate)
    g.complete(_req())
    with pytest.raises(BudgetExceededError):
        g.complete(_req())
    assert inner.calls == 2  # second call still happened (already in flight)
