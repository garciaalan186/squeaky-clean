"""BudgetedGateway: LLMGateway wrapper that gates each call's cost."""

from collections.abc import Callable

from squeaky_clean.application.use_cases.cost_gate import CostGate
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

CostEstimator = Callable[[LLMRequest], float]


class BudgetedGateway(LLMGateway):
    """Delegates to an inner gateway; gates ``cost_usd`` through a CostGate.

    When an ``estimator`` is supplied, the projected cost is RESERVED against
    the cap BEFORE the call — so a call that would blow the budget raises
    BudgetExceededError without being paid for — then reconciled to the actual
    cost afterward. Without an estimator it falls back to post-hoc recording.
    Either way BudgetExceededError bubbles up to the pipeline, which converts
    it into a graceful partial-results exit.
    """

    def __init__(
        self, inner: LLMGateway, gate: CostGate,
        estimator: CostEstimator | None = None,
    ) -> None:
        self._inner: LLMGateway = inner
        self._gate: CostGate = gate
        self._estimator: CostEstimator | None = estimator

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Reserve projected cost, forward to inner, settle actual cost."""
        if self._estimator is None:
            response = self._inner.complete(request)
            self._gate.record(response.cost_usd)
            return response
        reserved = self._gate.reserve(self._estimator(request))
        actual = 0.0
        try:
            response = self._inner.complete(request)
            actual = response.cost_usd
            return response
        finally:
            self._gate.settle(reserved, actual)

    def gate(self) -> CostGate:
        """Return the wrapped CostGate (for inspection/reporting)."""
        return self._gate
