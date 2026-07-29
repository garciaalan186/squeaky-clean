"""ModelRoutingPolicy port: resolve a ModelTier to a concrete model id."""

from abc import ABC, abstractmethod

from squeaky_clean.domain.value_objects.model_tier import ModelTier


class ModelRoutingPolicy(ABC):
    """Port for mapping a routing tier to a concrete model identifier.

    Application use cases depend on this abstraction; the concrete
    ``ModelRouter`` (infrastructure) implements it. This keeps the
    Dependency Rule intact — the application layer no longer names a
    concrete infrastructure adapter to talk about routing.
    """

    @abstractmethod
    def route(self, tier: ModelTier) -> str:
        """Return the model identifier configured for ``tier``."""
