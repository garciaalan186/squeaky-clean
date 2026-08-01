"""EntityLifecycle DTO: declarative entity state machine."""

from dataclasses import dataclass

from squeaky_clean.application.shared.mcda.state_transition import StateTransition


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
