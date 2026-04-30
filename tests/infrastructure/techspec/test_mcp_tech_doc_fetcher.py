"""Tests for MCPTechDocFetcher (H4)."""

import json

import pytest

from squeaky_clean.domain.interfaces.tech_doc_fetcher import (
    MCPNotConfiguredError,
    TechDocFetcher,
    TechDocFetchError,
)
from squeaky_clean.infrastructure.techspec.mcp_tech_doc_fetcher import (
    MCPTechDocFetcher,
)


class _StubFetcher(TechDocFetcher):
    def __init__(self, body: str) -> None:
        self.body = body
        self.last_url: str = ""

    def fetch(self, url: str) -> str:
        self.last_url = url
        return self.body


def test_mcp_raises_when_env_var_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLEAN_AGENT_TECHSPEC_MCP_URL", raising=False)
    with pytest.raises(MCPNotConfiguredError):
        MCPTechDocFetcher().fetch("blob_storage/x/v1.json")


def test_mcp_returns_body_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CLEAN_AGENT_TECHSPEC_MCP_URL", "https://mcp.internal",
    )
    inner = _StubFetcher(json.dumps({"ok": True}))
    body = MCPTechDocFetcher(inner=inner).fetch("blob_storage/x/v1.json")
    assert json.loads(body) == {"ok": True}
    assert inner.last_url == "https://mcp.internal/blob_storage/x/v1.json"


def test_mcp_rejects_non_json_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CLEAN_AGENT_TECHSPEC_MCP_URL", "https://mcp.internal",
    )
    inner = _StubFetcher("<html>not json</html>")
    with pytest.raises(TechDocFetchError):
        MCPTechDocFetcher(inner=inner).fetch("blob_storage/x/v1.json")
