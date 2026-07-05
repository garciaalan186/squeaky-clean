"""RefactorDecider: pick preserve-vs-split under the user's criteria weights."""

from squeaky_clean.application.dtos.recovery.decomposition_option import (
    DecompositionOption,
)
from squeaky_clean.application.dtos.recovery.tradeoff_outcome import TradeoffOutcome
from squeaky_clean.application.use_cases.recovery.architectural_tradeoff_scorer import (
    ArchitecturalTradeoffScorer,
)

_PRESERVE = DecompositionOption(
    name="preserve",
    scores={
        "testability": 2, "simplicity": 5, "performance": 4,
        "evolvability": 2, "migration_safety": 5, "delivery_speed": 5,
    },
    description="Keep the framework-coupled class as an Active-Record "
                "boundary object; lowest churn, highest coupling.",
)
_SPLIT = DecompositionOption(
    name="split",
    scores={
        "testability": 5, "simplicity": 2, "performance": 3,
        "evolvability": 5, "migration_safety": 2, "delivery_speed": 2,
    },
    description="Extract a pure Entity behind a Repository port with a "
                "framework Adapter; highest purity, highest churn.",
)


class RefactorDecider:
    """Decides whether recovery should preserve or split coupled classes.

    The preserve-vs-split trade-off is generic — splitting buys testability
    and evolvability at the cost of simplicity, migration-safety, and
    delivery speed — so both options carry canonical criterion profiles.
    Scoring them under the user's rank-order-centroid weights yields the
    recommendation, with near-ties flagged for the human review gate.
    """

    def __init__(self) -> None:
        self._scorer: ArchitecturalTradeoffScorer = ArchitecturalTradeoffScorer()

    def decide(self, weights: dict[str, float]) -> TradeoffOutcome:
        """Return the preserve-vs-split outcome under ``weights``."""
        return self._scorer.rank((_PRESERVE, _SPLIT), weights)
