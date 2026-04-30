"""InfrastructureChoice DTO: a (category, technology, version_pin) triple."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InfrastructureChoice:
    """One explicit infrastructure pin from a ProblemSpec."""

    category: str
    technology: str
    version_pin: str

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("InfrastructureChoice.category is empty")
        if not self.technology:
            raise ValueError("InfrastructureChoice.technology is empty")
        if not self.version_pin:
            raise ValueError("InfrastructureChoice.version_pin is empty")
