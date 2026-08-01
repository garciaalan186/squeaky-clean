"""GitInfo port: abstract interface for version-control provenance."""

from abc import ABC, abstractmethod


class GitInfo(ABC):
    """Port for reading the framework checkout's git provenance.

    R6.4c: the application layer must stay subprocess-free, so the
    ``git rev-parse`` call lives in an infrastructure adapter behind
    this port. Consumers treat the SHA as an opaque provenance string
    (``"unknown"`` when the checkout state cannot be determined).
    """

    @abstractmethod
    def head_sha(self) -> str:
        """Return the current HEAD commit SHA, or ``"unknown"``."""
