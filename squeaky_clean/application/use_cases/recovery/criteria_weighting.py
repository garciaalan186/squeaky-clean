"""CriteriaWeighting: turn a user criterion ranking into MCDA weights."""

from squeaky_clean.application.dtos.recovery.architectural_criterion import (
    ALL_ARCHITECTURAL_CRITERIA,
)


class CriteriaWeighting:
    """Converts an importance ranking into rank-order-centroid weights.

    The user supplies criteria most-important first. Rank-order centroid
    assigns ``w_i = (1/n) * sum_{k=i..n} 1/k`` — weights that already sum to
    1.0, give the top rank markedly more pull than rank-sum, and depend only
    on the ordering (no magnitude guessing). Deterministic; no LLM.
    """

    def from_ranking(self, ordered: tuple[str, ...]) -> dict[str, float]:
        """Return {criterion: weight} from a most-important-first ranking."""
        unknown = [c for c in ordered if c not in ALL_ARCHITECTURAL_CRITERIA]
        if unknown:
            raise ValueError(f"unknown criteria: {unknown}")
        if len(set(ordered)) != len(ordered):
            raise ValueError("ranking has duplicate criteria")
        n = len(ordered)
        if n == 0:
            raise ValueError("ranking is empty")
        return {
            crit: sum(1.0 / k for k in range(i, n + 1)) / n
            for i, crit in enumerate(ordered, start=1)
        }
