"""ArchitecturalTradeoffScorer: weighted-sum MCDA over decomposition options."""

from squeaky_clean.application.dtos.recovery.decomposition_option import (
    DecompositionOption,
)
from squeaky_clean.application.dtos.recovery.tradeoff_outcome import TradeoffOutcome

_CLOSE_MARGIN: float = 0.5


class ArchitecturalTradeoffScorer:
    """Ranks decomposition options by weighted criterion score.

    Infeasible options (hard-gate failures) are dropped before scoring, so
    an architectural violation is never traded away for a high weighted
    score. The winner is the top feasible option; when its lead over the
    runner-up is under half a weighted point the outcome is flagged
    ``close`` for the review gate. Deterministic tie-break by name.
    """

    def rank(
        self,
        options: tuple[DecompositionOption, ...],
        weights: dict[str, float],
    ) -> TradeoffOutcome:
        """Return the ranked TradeoffOutcome over the feasible options."""
        feasible = [o for o in options if o.feasible]
        if not feasible:
            raise ValueError("no feasible options to rank")
        scored = sorted(
            ((o.name, self._score(o, weights)) for o in feasible),
            key=lambda row: (-row[1], row[0]),
        )
        margin = scored[0][1] - scored[1][1] if len(scored) > 1 else float("inf")
        return TradeoffOutcome(
            ranked=tuple(scored), winner=scored[0][0],
            margin=round(margin, 6), close=margin < _CLOSE_MARGIN,
        )

    def _score(self, option: DecompositionOption, weights: dict[str, float]) -> float:
        return round(
            sum(option.scores.get(c, 0) * w for c, w in weights.items()), 6,
        )
