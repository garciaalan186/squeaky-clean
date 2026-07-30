"""LLMGatewayError: raised when an LLMGateway adapter cannot fulfil a call."""


class LLMGatewayError(RuntimeError):
    """Raised when an LLMGateway adapter fails to complete a request.

    ``retryable`` marks *transient* transport faults (a failed spawn, an empty
    non-zero exit, malformed result JSON) that a wrapping RetryingGateway may
    safely re-attempt. Genuine model-level errors (``is_error: true``) leave it
    False so they surface immediately instead of burning the retry budget.
    """

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable: bool = retryable
