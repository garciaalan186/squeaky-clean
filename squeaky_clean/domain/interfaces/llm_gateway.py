"""LLMGateway port: abstract interface for LLM completion calls."""

from abc import ABC, abstractmethod

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class LLMGateway(ABC):
    """Port for sending a prompt to an LLM and receiving a completion."""

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Submit the request and return a completed LLMResponse."""
