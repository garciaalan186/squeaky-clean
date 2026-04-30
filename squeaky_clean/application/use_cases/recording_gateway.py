"""RecordingGateway: LLMGateway wrapper that records every call."""

from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class RecordingGateway(LLMGateway):
    """Delegates to an inner gateway and records each response."""

    def __init__(self, inner: LLMGateway, recorder: LLMUsageRecorder) -> None:
        self._inner: LLMGateway = inner
        self._recorder: LLMUsageRecorder = recorder
        self._label: str = "security_icp"

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Forward to inner gateway and record the response."""
        response = self._inner.complete(request)
        self._recorder.record(response, self._label)
        return response
