"""MCPTechDocFetcher: env-configurable MCP-server fetcher (H4)."""

import json
import os

from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher
from squeaky_clean.domain.interfaces.techspec.mcp_not_configured_error import (
    MCPNotConfiguredError,
)
from squeaky_clean.domain.interfaces.techspec.tech_doc_fetch_error import (
    TechDocFetchError,
)

_ENV_VAR: str = "CLEAN_AGENT_TECHSPEC_MCP_URL"


class MCPTechDocFetcher(TechDocFetcher):
    """Reads techspec JSON from the configured MCP URL or raises.

    ``inner`` (the transport) is REQUIRED: it is an I/O-touching
    collaborator, so the composition root must inject it explicitly
    (R6.12 — no impure ``or Default()`` fallback).
    """

    def __init__(self, inner: TechDocFetcher) -> None:
        self._inner: TechDocFetcher = inner

    def fetch(self, url: str) -> str:
        """Fetch via MCP base; require JSON body. Raises on misconfiguration."""
        base = os.environ.get(_ENV_VAR)
        if not base:
            raise MCPNotConfiguredError(
                f"{_ENV_VAR} is not set; MCP source disabled"
            )
        full = self._compose_url(base, url)
        body = self._inner.fetch(full)
        try:
            json.loads(body)
        except json.JSONDecodeError as exc:
            raise TechDocFetchError(
                f"MCP response not valid JSON: {exc}"
            ) from exc
        return body

    @staticmethod
    def _compose_url(base: str, suffix: str) -> str:
        if suffix.startswith(("http://", "https://")):
            return suffix
        return base.rstrip("/") + "/" + suffix.lstrip("/")
