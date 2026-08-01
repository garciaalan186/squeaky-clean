"""InfrastructureChoiceArchitect: MCDA winner + Manager-tier rationale (H3)."""

from __future__ import annotations

from squeaky_clean.application.generation.techspec.derived_infrastructure_choice import (
    DerivedInfrastructureChoice,
)
from squeaky_clean.application.generation.techspec.no_candidates_available_error import (
    NoCandidatesAvailableError,
)
from squeaky_clean.application.shared.mcda.mcda_registry import MCDARegistry
from squeaky_clean.application.shared.mcda.mcda_score_row import MCDAScoreRow
from squeaky_clean.application.shared.mcda.mcda_score_table import MCDAScoreTable
from squeaky_clean.application.shared.mcda.mcda_scorer import MCDAScorer
from squeaky_clean.application.shared.mcda.mcda_weights import MCDAWeights
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_RATIONALE_WORD_LIMIT: int = 50


class InfrastructureChoiceArchitect:
    """Manager-tier agent: MCDA + ≤50-word rationale per category."""

    def __init__(
        self, gateway: LLMGateway, registry: MCDARegistry,
        routing: ModelRoutingPolicy,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._registry: MCDARegistry = registry
        self._routing: ModelRoutingPolicy = routing

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
        table = MCDAScorer(weights).score(category, candidates)
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
            model=self._routing.route(ModelTier.MANAGER),
            system_prompt="MCDA rationale writer.",
            user_prompt=prompt, temperature=0.0, tier="manager",
        )
        text = self._gateway.complete(req).content.strip()
        return self._truncate(text, _RATIONALE_WORD_LIMIT)

    @staticmethod
    def _truncate(text: str, max_words: int) -> str:
        words = text.split()
        return text if len(words) <= max_words else " ".join(words[:max_words])
