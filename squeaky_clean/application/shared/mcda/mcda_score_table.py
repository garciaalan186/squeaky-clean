"""MCDAScoreTable: deterministic ranking of candidate technologies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MCDAScoreRow:
    """One candidate technology's per-criterion scores + weighted total."""

    technology: str
    version_pin: str
    scores: dict[str, int]
    weighted_score: float


@dataclass(frozen=True)
class MCDAScoreTable:
    """Per-category MCDA result: ordered candidates + weights used."""

    category: str
    candidates: tuple[MCDAScoreRow, ...]
    weights: dict[str, float]

    def winner(self) -> MCDAScoreRow:
        """Return the highest-scoring candidate (first row)."""
        if not self.candidates:
            raise ValueError(f"MCDAScoreTable for {self.category!r} is empty")
        return self.candidates[0]
