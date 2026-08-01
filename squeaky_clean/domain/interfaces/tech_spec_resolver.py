"""TechSpecResolver port: maps (category, technology, version) to a TechSpec."""

from abc import ABC, abstractmethod

from squeaky_clean.domain.value_objects.tech_spec import TechSpec


class TechSpecUnresolvableError(RuntimeError):
    """Raised when no source can produce a valid TechSpec for the triple."""


class TechSpecResolutionError(TechSpecUnresolvableError):
    """TechSpecUnresolvableError that carries per-source failure reasons (R6.8).

    Subclasses the port error so existing ``except TechSpecUnresolvableError``
    sites keep working, while callers (and the JSON event log) see WHY every
    source failed instead of a silent degrade.
    """

    def __init__(self, message: str, reasons: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.reasons: tuple[str, ...] = reasons


class TechSpecResolver(ABC):
    """Abstract resolver. Implementations may consult disk, MCP, or web."""

    @abstractmethod
    def resolve(
        self, category: str, technology: str, version: str,
    ) -> TechSpec:
        """Return a validated TechSpec; raise TechSpecUnresolvableError on miss."""
        raise NotImplementedError
