"""DecompositionOption DTO: one candidate architectural choice for MCDA."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecompositionOption:
    """A candidate decomposition/refactor choice scored against criteria.

    `scores` maps each architectural criterion to a 1-5 rating for this
    option. `feasible` encodes the hard-gate result: an option violating a
    non-negotiable invariant (Dependency Rule, SOLID, acyclicity) is marked
    infeasible and excluded before any weighted scoring, so a high weighted
    score can never buy back an architectural violation.
    """

    name: str
    scores: dict[str, int]
    feasible: bool = True
    description: str = field(default="")
