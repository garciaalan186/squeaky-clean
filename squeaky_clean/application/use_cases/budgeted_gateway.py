"""BudgetedGateway: LLMGateway wrapper that records each call's cost."""

from squeaky_clean.application.use_cases.cost_gate import CostGate
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class BudgetedGateway(LLMGateway):
    """Delegates to an inner gateway; routes ``cost_usd`` through a CostGate.

    Records actual spend after each successful call. The gate raises
    BudgetExceededError once the cumulative total trips the configured cap;
    that exception bubbles up to the pipeline, which converts it into a
    graceful partial-results exit.
    """

    def __init__(self, inner: LLMGateway, gate: CostGate) -> None:
        self._inner: LLMGateway = inner
        self._gate: CostGate = gate

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Forward to inner gateway and record the response's cost."""
        response = self._inner.complete(request)
        self._gate.record(response.cost_usd)
        return response

    def gate(self) -> CostGate:
        """Return the wrapped CostGate (for inspection/reporting)."""
        return self._gate
