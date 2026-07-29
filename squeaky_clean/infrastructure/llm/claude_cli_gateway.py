"""ClaudeCLIGateway: LLMGateway adapter that shells out to `claude -p`."""

import logging
import os
import signal
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
            stdout, returncode = self._run(argv)
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
            raise LLMGatewayError(
                f"claude CLI timed out: {exc}", retryable=True,
            ) from exc
        except OSError as exc:
            raise LLMGatewayError(
                f"failed to invoke claude CLI: {exc}", retryable=True,
            ) from exc
        if returncode != 0:
            # An empty exit is a transient hiccup worth retrying; a non-empty
            # one carries a genuine diagnostic and should surface immediately.
            raise LLMGatewayError(
                f"claude CLI exit {returncode}: {stdout[:500]}",
                retryable=not stdout.strip(),
            )
        return self._parser.parse(stdout)

    def _run(self, argv: list[str]) -> tuple[str, int]:
        """Spawn the CLI in its own session; kill the group on timeout.

        ``subprocess.run`` only signals the direct child, orphaning any
        grandchildren the CLI spawns. Starting a new session and killing the
        whole process group on timeout prevents leaked workers.
        """
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, _stderr = proc.communicate(timeout=self._timeout)
        except subprocess.TimeoutExpired:
            self._kill_group(proc)
            proc.communicate()
            raise
        return stdout, proc.returncode

    @staticmethod
    def _kill_group(proc: "subprocess.Popen[str]") -> None:
        """Best-effort SIGKILL of the child's process group."""
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()

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
