"""ClaudeCLIGateway: LLMGateway adapter that shells out to `claude -p`."""

import logging
import subprocess

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.cli_command_builder import CLICommandBuilder
from squeaky_clean.infrastructure.llm.cli_response_parser import CLIResponseParser
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError

_TIMEOUT_SECONDS: int = 240
_LOG = logging.getLogger(__name__)


class ClaudeCLIGateway(LLMGateway):
    """Calls the local `claude` CLI in JSON mode and maps its output."""

    def __init__(
        self,
        binary_path: str = "claude",
        graceful_timeout: bool = True,
        timeout_seconds: int = _TIMEOUT_SECONDS,
    ) -> None:
        self._builder: CLICommandBuilder = CLICommandBuilder(binary_path)
        self._parser: CLIResponseParser = CLIResponseParser()
        self._graceful: bool = graceful_timeout
        self._timeout: int = timeout_seconds

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Run `claude -p` for this request and return the parsed response."""
        self._warn_if_unsupported(request)
        argv = self._builder.build(request)
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            if self._graceful:
                return LLMResponse(
                    content="",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    duration_ms=self._timeout * 1000,
                    timed_out=True,
                )
            raise LLMGatewayError(f"claude CLI timed out: {exc}") from exc
        except OSError as exc:
            raise LLMGatewayError(f"failed to invoke claude CLI: {exc}") from exc
        if completed.returncode != 0:
            raise LLMGatewayError(
                f"claude CLI exit {completed.returncode}: {completed.stderr}"
            )
        return self._parser.parse(completed.stdout)

    @staticmethod
    def _warn_if_unsupported(request: LLMRequest) -> None:
        """`claude -p` has no --temperature/--seed flags; log if requested."""
        if request.temperature is not None:
            _LOG.warning(
                "claude CLI ignores temperature=%s (no --temperature flag); "
                "use AnthropicSDKGateway for sampling control",
                request.temperature,
            )
        if request.seed is not None:
            _LOG.warning(
                "claude CLI ignores seed=%s (no --seed flag); "
                "use AnthropicSDKGateway for seed control",
                request.seed,
            )
