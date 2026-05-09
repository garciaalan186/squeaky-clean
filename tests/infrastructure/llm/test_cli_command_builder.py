"""Tests for CLICommandBuilder."""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.cli_command_builder import CLICommandBuilder


def test_build_argv_matches_expected_order() -> None:
    request = LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS",
        user_prompt="USER",
    )
    argv = CLICommandBuilder().build(request)
    assert argv[0] == "claude"
    assert argv[1:3] == ["-p", "USER"]
    assert "--model" in argv and argv[argv.index("--model") + 1] == request.model
    assert "--system-prompt" in argv
    assert argv[argv.index("--system-prompt") + 1] == "SYS"
    assert "--output-format" in argv
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "--disallowedTools" in argv


def test_custom_binary_path() -> None:
    request = LLMRequest(model="m", system_prompt="s", user_prompt="u")
    argv = CLICommandBuilder(binary_path="/tmp/claude").build(request)
    assert argv[0] == "/tmp/claude"
