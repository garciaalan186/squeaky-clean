"""MCDAScoreTable: deterministic ranking of candidate technologies."""

from dataclasses import dataclass

# Re-export: mcda_scorer (owned by a parallel batch) still imports the row
# type from this module; the class now lives in its own file.
from squeaky_clean.application.shared.mcda.mcda_score_row import (
    MCDAScoreRow as MCDAScoreRow,
)


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
