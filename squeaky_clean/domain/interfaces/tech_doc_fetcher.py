"""TechDocFetcher port: fetch raw documentation bodies from a URL (H4)."""

from abc import ABC, abstractmethod


class TechDocFetcher(ABC):
    """Abstract port: returns the raw text body for a URL or raises."""

    @abstractmethod
    def fetch(self, url: str) -> str:
        """Return the raw text body, or raise TechDocFetchError."""
        raise NotImplementedError
