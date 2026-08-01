"""ICPRetryHandler: bounded ICP retry wrapper with exponential backoff."""

import time

from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_RETRY_SUFFIX: str = (
    "\n\nRETRY: Your previous output could not be parsed. Error: {err}\n"
    "Please emit ONLY a single fenced code block containing the class"
    " implementation. No prose outside the fence."
)


class ICPRetryHandler:
    """Retries an ICP LLM call up to ``policy.max_icp_retries`` times."""

    def __init__(
        self, gateway: LLMGateway, policy: RetryPolicy | None = None,
        parser: ParseImplementedClass | None = None,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._policy: RetryPolicy = policy or RetryPolicy()  # pure default (config VO)
        self._parser = parser or ParseImplementedClass()  # pure default (parser)

    def run(
        self, request: LLMRequest, class_name: str,
    ) -> tuple[LLMResponse, int]:
        """Issue the call; on timeout/parse failure, retry with backoff."""
        first = self._gateway.complete(request)
        last_err = self._failure(first, class_name)
        if last_err is None:
            return first, 0
        response = first
        for attempt in range(self._policy.max_icp_retries):
            self._sleep(attempt)
            response = self._gateway.complete(self._build(request, last_err))
            last_err = self._failure(response, class_name)
            if last_err is None:
                return response, attempt + 1
        return response, self._policy.max_icp_retries

    def _failure(self, response: LLMResponse, class_name: str) -> str | None:
        """Return a retryable error string, or None if the response is usable."""
        if response.timed_out:
            return "previous call timed out before returning content"
        return self._try_parse(response.content, class_name)

    def _try_parse(self, content: str, class_name: str) -> str | None:
        try:
            self._parser.parse(content, class_name)
            return None
        except ImplementedClassParseError as exc:
            return str(exc)

    def _build(self, request: LLMRequest, err: str) -> LLMRequest:
        return LLMRequest(
            model=request.model,
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt + _RETRY_SUFFIX.format(err=err),
            temperature=request.temperature,
            seed=request.seed,
            replicate_id=request.replicate_id,
            tier=request.tier,
            cacheable_user_prefix=request.cacheable_user_prefix,
            max_tokens=request.max_tokens,
        )

    def _sleep(self, attempt: int) -> None:
        delay = self._policy.delay_for(attempt)
        if delay > 0:
            time.sleep(delay)
