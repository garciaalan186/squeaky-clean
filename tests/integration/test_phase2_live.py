"""Live integration smoke test: one Haiku call through ClaudeCLIGateway."""

import os

import pytest

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway

_SKIP_REASON = "Set RUN_INTEGRATION_TESTS=1 to enable live LLM calls"


@pytest.mark.integration
def test_claude_cli_gateway_live_roundtrip() -> None:
    if os.environ.get("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip(_SKIP_REASON)
    gateway = ClaudeCLIGateway()
    request = LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt=(
            "You are a terse responder. Output ONLY the exact §Notation block "
            "below with no extra text and no markdown fences."
        ),
        user_prompt=(
            "Echo this notation verbatim:\n"
            "MODULE Ping\nLAYER Domain\nEXPORTS [Ping]\nDEPENDS []\n"
            "CLASSES {\n  Ping -> SimpleClass { methods: [] }\n}\n"
            "INVARIANTS []\n"
        ),
    )
    response = gateway.complete(request)
    assert response.content
    assert response.duration_ms > 0
    print(
        f"\n[live] duration_ms={response.duration_ms} "
        f"cost_usd={response.cost_usd} "
        f"input_tokens={response.input_tokens} "
        f"output_tokens={response.output_tokens}"
    )
    print("[live] content:\n" + response.content)
