"""MCDARegistryEntryMissingError: category has no candidates on disk."""

from __future__ import annotations


class MCDARegistryEntryMissingError(KeyError):
    """Raised when a category has no registered candidates on disk."""
