"""CLICommandBuilder: assemble argv for the `claude -p` CLI invocation."""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest

_DISALLOWED_TOOLS: str = "Bash,Edit,Write,Read,Glob,Grep,Agent"


class CLICommandBuilder:
    """Produces the subprocess argv list for a ClaudeCLIGateway request."""

    def __init__(self, binary_path: str = "claude") -> None:
        self._binary: str = binary_path

    def build(self, request: LLMRequest) -> list[str]:
        """Return the argv list that invokes `claude -p` for this request."""
        return [
            self._binary,
            "-p",
            request.user_prompt,
            "--model",
            request.model,
            "--output-format",
            "json",
            "--system-prompt",
            request.system_prompt,
            "--disallowedTools",
            _DISALLOWED_TOOLS,
        ]
