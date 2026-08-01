"""MCPNotConfiguredError: MCP fetcher invoked without MCP configuration."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.techspec.tech_doc_fetch_error import (
    TechDocFetchError,
)


class MCPNotConfiguredError(TechDocFetchError):
    """Raised when an MCP fetcher is invoked without MCP configuration."""
