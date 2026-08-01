"""TechDocFetchError: documentation fetch failed (network / non-200 / size)."""

from __future__ import annotations


class TechDocFetchError(RuntimeError):
    """Raised on any network failure, non-200 response, or oversize body."""
