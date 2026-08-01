"""MCDAScorer: deterministic weighted-score ranking of MCDA candidates."""

from __future__ import annotations

from squeaky_clean.application.shared.mcda.mcda_criterion import ALL_MCDA_CRITERIA
from squeaky_clean.application.shared.mcda.mcda_registry import MCDARegistryEntry
from squeaky_clean.application.shared.mcda.mcda_score_table import MCDAScoreRow, MCDAScoreTable

_STABILITY_RANK: dict[str, int] = {"ga": 0, "beta": 1, "preview": 2}


class MCDAScorer:
    """Pure MCDA scorer for ONE evaluation's weights (8 criteria;
    deterministic tie-breaks). Construct per problem — weights and
    override list are evaluation state, not call arguments (R6.11b)."""

    def __init__(
        self, weights: dict[str, float],
        problem_overrides: tuple[str, ...] = (),
    ) -> None:
        self._weights: dict[str, float] = weights
        self._overrides: tuple[str, ...] = problem_overrides

    def score(
        self, category: str, candidates: tuple[MCDARegistryEntry, ...],
    ) -> MCDAScoreTable:
        """Return an MCDAScoreTable sorted by weighted_score desc."""
        rows = tuple(self._row(c, self._weights) for c in candidates)
        stability = {c.technology: c.stability for c in candidates}
        ordered = sorted(
            rows,
            key=lambda r: self._sort_key(r, self._overrides, stability),
        )
        return MCDAScoreTable(
            category=category, candidates=tuple(ordered),
            weights=dict(self._weights),
        )

    @staticmethod
    def _row(
        c: MCDARegistryEntry, weights: dict[str, float],
    ) -> MCDAScoreRow:
        scores = {k: int(c.scores.get(k, 0)) for k in ALL_MCDA_CRITERIA}
        weighted = sum(scores[k] * float(weights.get(k, 0.0))
                       for k in ALL_MCDA_CRITERIA)
        return MCDAScoreRow(
            technology=c.technology, version_pin=c.version_pin,
            scores=scores, weighted_score=round(weighted, 6),
        )

    @staticmethod
    def _sort_key(
        row: MCDAScoreRow, prefs: tuple[str, ...], stab: dict[str, str],
    ) -> tuple[float, int, int, str]:
        pref_rank = (prefs.index(row.technology)
                     if row.technology in prefs else len(prefs))
        s_rank = _STABILITY_RANK.get(stab.get(row.technology, "ga"), 99)
        return (-row.weighted_score, pref_rank, s_rank, row.technology)
