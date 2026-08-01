"""Tests for MCPNotConfiguredError."""

import pytest

from squeaky_clean.domain.interfaces.techspec.mcp_not_configured_error import (
    MCPNotConfiguredError,
)
from squeaky_clean.domain.interfaces.techspec.tech_doc_fetch_error import (
    TechDocFetchError,
)


def test_is_a_tech_doc_fetch_error() -> None:
    assert issubclass(MCPNotConfiguredError, TechDocFetchError)


def test_catchable_as_fetch_error() -> None:
    with pytest.raises(TechDocFetchError):
        raise MCPNotConfiguredError("MCP fetcher invoked without configuration")
