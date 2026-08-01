"""TechDocFormatUnknownError: no doc-site extractor matched the HTML."""

from __future__ import annotations


class TechDocFormatUnknownError(RuntimeError):
    """Raised when no extractor matches the HTML."""
