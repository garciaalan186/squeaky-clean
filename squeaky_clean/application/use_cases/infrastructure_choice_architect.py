"""InfrastructureChoiceArchitect: MCDA winner + Manager-tier rationale (H3)."""

from __future__ import annotations

from squeaky_clean.application.dtos.derived_infrastructure_choice import (
    DerivedInfrastructureChoice,
)
from squeaky_clean.application.dtos.mcda_score_table import MCDAScoreRow, MCDAScoreTable
from squeaky_clean.application.dtos.mcda_weights import MCDAWeights
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.mcda_registry import MCDARegistry
from squeaky_clean.application.use_cases.mcda_scorer import MCDAScorer
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest

_RATIONALE_WORD_LIMIT: int = 50
_MANAGER_MODEL: str = "claude-sonnet-4-5"


class NoCandidatesAvailableError(LookupError):
    """Raised when the MCDA registry returns zero candidates."""


class InfrastructureChoiceArchitect:
    """Manager-tier agent: MCDA + ≤50-word rationale per category."""

    def __init__(
        self, gateway: LLMGateway, registry: MCDARegistry, scorer: MCDAScorer,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._registry: MCDARegistry = registry
        self._scorer: MCDAScorer = scorer

    def decide(
        self, problem: ProblemSpec, category: str,
    ) -> DerivedInfrastructureChoice:
        """Return the winning DerivedInfrastructureChoice for ``category``."""
        candidates = self._registry.candidates(category)
        if not candidates:
            raise NoCandidatesAvailableError(category)
        weights = (
            MCDAWeights.from_mapping(problem.mcda_weights).as_dict()
            if problem.mcda_weights else MCDAWeights().as_dict()
        )
        table = self._scorer.score(category, candidates, weights, ())
        winner = table.winner()
        rationale = self._rationale(table, winner)
        return DerivedInfrastructureChoice(
            category=category, technology=winner.technology,
            version_pin=winner.version_pin, scores=dict(winner.scores),
            weighted_score=winner.weighted_score, rationale=rationale,
        )

    def _rationale(
        self, table: MCDAScoreTable, winner: MCDAScoreRow,
    ) -> str:
        prompt = (
            f"Category: {table.category}. Winner: {winner.technology} "
            f"(score={winner.weighted_score:.2f}, scores={winner.scores}). "
            f"Write a single ≤{_RATIONALE_WORD_LIMIT}-word rationale; "
            f"no preamble, no markdown."
        )
        req = LLMRequest(
            model=_MANAGER_MODEL, system_prompt="MCDA rationale writer.",
            user_prompt=prompt, temperature=0.0, tier="manager",
        )
        text = self._gateway.complete(req).content.strip()
        return self._truncate(text, _RATIONALE_WORD_LIMIT)

    @staticmethod
    def _truncate(text: str, max_words: int) -> str:
        words = text.split()
        return text if len(words) <= max_words else " ".join(words[:max_words])
