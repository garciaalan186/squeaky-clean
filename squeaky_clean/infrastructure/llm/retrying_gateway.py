"""RetryingGateway: retry transient transport failures at every tier."""

import logging
import random
import time
from collections.abc import Callable

from squeaky_clean.application.dtos.retry_policy import RetryPolicy
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError

_LOG = logging.getLogger(__name__)


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
    ) -> None:
        self._inner: LLMGateway = inner
        self._policy: RetryPolicy = policy or RetryPolicy()
        self._sleep: Callable[[float], None] = sleep
        self._rand: Callable[[], float] = rand

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
        _LOG.warning(
            "gateway retry %d/%d after %s (sleeping %.2fs)",
            attempt + 1, self._policy.max_transport_retries, reason, delay,
        )
        if delay > 0:
            self._sleep(delay)
