"""EntityLifecycle DTO: declarative entity state machine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StateTransition:
    """One transition in an entity state machine."""

    from_state: str
    to_state: str
    trigger: str

    def __post_init__(self) -> None:
        """Reject empty fields."""
        if not self.from_state:
            raise ValueError("StateTransition.from_state must be non-empty")
        if not self.to_state:
            raise ValueError("StateTransition.to_state must be non-empty")
        if not self.trigger:
            raise ValueError("StateTransition.trigger must be non-empty")


@dataclass(frozen=True)
class EntityLifecycle:
    """A named entity plus its tuple of allowed state transitions."""

    entity: str
    transitions: tuple[StateTransition, ...]

    def __post_init__(self) -> None:
        """Reject empty entity name and empty transitions tuple."""
        if not self.entity:
            raise ValueError("EntityLifecycle.entity must be non-empty")
        if not self.transitions:
            raise ValueError(
                "EntityLifecycle.transitions must contain at least one transition"
            )
