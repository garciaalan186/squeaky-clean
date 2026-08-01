"""MCDAScoreRow: one candidate technology's scores + weighted total."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MCDAScoreRow:
    """One candidate technology's per-criterion scores + weighted total."""

    technology: str
    version_pin: str
    scores: dict[str, int]
    weighted_score: float
