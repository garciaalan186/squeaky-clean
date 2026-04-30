"""DerivedInfrastructureChoice: MCDA-derived infrastructure pick + rationale."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice


@dataclass(frozen=True)
class DerivedInfrastructureChoice:
    """One MCDA-derived (category, technology, version_pin) pick.

    Mirrors :class:`InfrastructureChoice` and adds the score breakdown +
    weighted total + a ≤50-word LLM-generated rationale.
    """

    category: str
    technology: str
    version_pin: str
    scores: dict[str, int]
    weighted_score: float
    rationale: str

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("DerivedInfrastructureChoice.category is empty")
        if not self.technology:
            raise ValueError("DerivedInfrastructureChoice.technology is empty")
        if not self.version_pin:
            raise ValueError("DerivedInfrastructureChoice.version_pin is empty")

    def to_choice(self) -> InfrastructureChoice:
        """Collapse into the canonical InfrastructureChoice shape."""
        return InfrastructureChoice(
            category=self.category, technology=self.technology,
            version_pin=self.version_pin,
        )
