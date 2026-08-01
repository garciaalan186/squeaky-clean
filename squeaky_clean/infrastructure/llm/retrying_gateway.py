"""RetryingGateway: retry transient transport failures at every tier."""

import random
import time
from collections.abc import Callable

from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


class RetryingGateway(LLMGateway):
    """Wraps a gateway and re-attempts *transient* failures with jittered backoff.

    Distinct from ``ICPRetryHandler`` (which retries *parse* failures with
    corrective feedback): this is the transport layer, shared by ALL tiers
    (architect, testgen, manager, ICP, fixer). It retries a retryable
    ``LLMGatewayError`` or a graceful timeout, then hands the last outcome up
    unchanged so parse-retry and the ``agent_hangs`` accounting still apply.
    """

    def __init__(
        self,
        inner: LLMGateway,
        policy: RetryPolicy | None = None,
        sleep: Callable[[float], None] = time.sleep,
        rand: Callable[[], float] = random.random,
        *,
        logger: RunLogger | None = None,
    ) -> None:
        self._inner: LLMGateway = inner
        self._policy: RetryPolicy = policy or RetryPolicy()  # pure default (config VO)
        self._sleep: Callable[[float], None] = sleep
        self._rand: Callable[[], float] = rand
        self._log: RunLogger = logger or NullRunLogger()

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Call the inner gateway, retrying transient faults up to the cap."""
        last: LLMResponse | None = None
        attempts = self._policy.max_transport_retries
        for attempt in range(attempts + 1):
            try:
                response = self._inner.complete(request)
            except LLMGatewayError as exc:
                if not exc.retryable or attempt == attempts:
                    raise
                self._backoff(attempt, f"transport error: {exc}")
                continue
            if response.timed_out and attempt < attempts:
                last = response
                self._backoff(attempt, "call timed out")
                continue
            return response
        # Only reached when the final attempt timed out gracefully.
        assert last is not None
        return last

    def _backoff(self, attempt: int, reason: str) -> None:
        delay = self._policy.jittered_delay_for(attempt, self._rand())
        self._log.event(
            "gateway_retry", attempt=attempt + 1,
            max_retries=self._policy.max_transport_retries,
            reason=reason, sleep_seconds=round(delay, 2),
        )
        if delay > 0:
            self._sleep(delay)
