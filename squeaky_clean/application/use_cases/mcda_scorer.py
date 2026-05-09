"""MCDAScorer: deterministic weighted-score ranking of MCDA candidates."""

from __future__ import annotations

from squeaky_clean.application.dtos.mcda_criterion import ALL_MCDA_CRITERIA
from squeaky_clean.application.dtos.mcda_score_table import MCDAScoreRow, MCDAScoreTable
from squeaky_clean.application.use_cases.mcda_registry import MCDARegistryEntry

_STABILITY_RANK: dict[str, int] = {"ga": 0, "beta": 1, "preview": 2}


class MCDAScorer:
    """Pure-function MCDA scorer (8 criteria; deterministic tie-breaks)."""

    def score(
        self, category: str,
        candidates: tuple[MCDARegistryEntry, ...],
        weights: dict[str, float],
        problem_overrides: tuple[str, ...] = (),
    ) -> MCDAScoreTable:
        """Return an MCDAScoreTable sorted by weighted_score desc."""
        rows = tuple(self._row(c, weights) for c in candidates)
        stability = {c.technology: c.stability for c in candidates}
        ordered = sorted(
            rows,
            key=lambda r: self._sort_key(r, problem_overrides, stability),
        )
        return MCDAScoreTable(
            category=category, candidates=tuple(ordered), weights=dict(weights),
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
