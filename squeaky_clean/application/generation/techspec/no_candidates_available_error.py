"""NoCandidatesAvailableError: MCDA registry returned zero candidates."""

from __future__ import annotations


class NoCandidatesAvailableError(LookupError):
    """Raised when the MCDA registry returns zero candidates."""
