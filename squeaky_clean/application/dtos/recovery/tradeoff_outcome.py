"""TradeoffOutcome DTO: the ranked result of an architectural MCDA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeoffOutcome:
    """Ranked outcome of scoring decomposition options against weights.

    `ranked` lists (option_name, weighted_score) best-first over the
    feasible options only. `winner` is the top option. `margin` is the
    weighted-score gap to the runner-up; `close` is true when that gap is
    small — the signal the review gate uses to surface a near-tie for
    human judgement instead of silently committing the winner.
    """

    ranked: tuple[tuple[str, float], ...]
    winner: str
    margin: float
    close: bool
