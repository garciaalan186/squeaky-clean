"""MCDAWeights: per-criterion weights for the MCDA scorer (design §3.2)."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.mcda_criterion import ALL_MCDA_CRITERIA

_EPSILON: float = 1e-6


@dataclass(frozen=True)
class MCDAWeights:
    """Frozen criterion-weight bundle. Defaults match design §3.2."""

    ops: float = 0.20
    cost: float = 0.20
    cold: float = 0.10
    thru: float = 0.15
    eco: float = 0.10
    reg: float = 0.05
    lic: float = 0.05
    team: float = 0.15

    def __post_init__(self) -> None:
        total = (
            self.ops + self.cost + self.cold + self.thru
            + self.eco + self.reg + self.lic + self.team
        )
        if abs(total - 1.0) > _EPSILON:
            raise ValueError(
                f"MCDAWeights must sum to 1.0 (within {_EPSILON}); got {total!r}"
            )

    def as_dict(self) -> dict[str, float]:
        """Return weights as a {criterion: weight} dict."""
        return {
            "ops": self.ops, "cost": self.cost, "cold": self.cold,
            "thru": self.thru, "eco": self.eco, "reg": self.reg,
            "lic": self.lic, "team": self.team,
        }

    @classmethod
    def from_mapping(cls, mapping: dict[str, float]) -> "MCDAWeights":
        """Build from a dict using only the 8 canonical criterion keys."""
        for k in mapping:
            if k not in ALL_MCDA_CRITERIA:
                raise ValueError(f"unknown MCDA criterion: {k!r}")
        return cls(**{k: float(mapping[k]) for k in mapping})
