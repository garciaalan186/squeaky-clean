"""TechSpecResolver port: maps a TechSpecTarget to a TechSpec."""

from abc import ABC, abstractmethod

# Re-exports: the error types now live in techspec/ (one class per file,
# R6.11b); infrastructure resolvers still import them from this module.
from squeaky_clean.domain.interfaces.techspec.tech_spec_resolution_error import (
    TechSpecResolutionError as TechSpecResolutionError,
)
from squeaky_clean.domain.interfaces.techspec.tech_spec_unresolvable_error import (
    TechSpecUnresolvableError as TechSpecUnresolvableError,
)
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget


class TechSpecResolver(ABC):
    """Abstract resolver. Implementations may consult disk, MCP, or web."""

    @abstractmethod
    def resolve(self, target: TechSpecTarget) -> TechSpec:
        """Return a validated TechSpec; raise TechSpecUnresolvableError on miss."""
        raise NotImplementedError
