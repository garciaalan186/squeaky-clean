"""TechSpecResolver port: maps (category, technology, version) to a TechSpec."""

from abc import ABC, abstractmethod

from squeaky_clean.application.dtos.tech_spec import TechSpec


class TechSpecUnresolvableError(RuntimeError):
    """Raised when no source can produce a valid TechSpec for the triple."""


class TechSpecResolver(ABC):
    """Abstract resolver. Implementations may consult disk, MCP, or web."""

    @abstractmethod
    def resolve(
        self, category: str, technology: str, version: str,
    ) -> TechSpec:
        """Return a validated TechSpec; raise TechSpecUnresolvableError on miss."""
        raise NotImplementedError
