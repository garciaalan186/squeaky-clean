"""TechSpecValidator port: validates a candidate TechSpec dict against schema."""

from abc import ABC, abstractmethod


class TechSpecValidator(ABC):
    """Abstract validator returning a tuple of violation messages.

    Empty tuple means the candidate is schema-valid.
    """

    @abstractmethod
    def validate(self, candidate: dict[str, object]) -> tuple[str, ...]:
        """Return a tuple of human-readable schema violations."""
        raise NotImplementedError
