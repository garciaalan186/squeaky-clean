"""PromptOptimizer: simple directed search for better ICP prompts.

Equivalent of DSPy's MIPROv2 in spirit: takes an ICP spec, a list of
fixtures (input prompt + expected class name), and a scorer; tries
N candidate prompt variants; returns the best by mean score. Cheaper
than full MIPROv2 because variants are explicitly enumerated rather
than bootstrapped, but sufficient for D1's local-objective gate.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.eval.agent_scorers.icp_scorer import ICPScorer
from squeaky_clean.eval.agent_scorers.prompt_candidate import PromptCandidate


@dataclass(frozen=True)
class OptimizationFixture:
    """One unit of test for the optimizer: prompt + expected emitted class."""

    name: str
    user_prompt: str
    expected_class: str


_OptimizationFixture = OptimizationFixture


class PromptOptimizer:
    """Search over prompt variants; pick the one with highest mean score."""

    def __init__(
        self, gateway: LLMGateway, model: str,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._model: str = model
        self._scorer: ICPScorer = ICPScorer()

    def evaluate(
        self,
        candidate_name: str,
        system_prompt: str,
        fixtures: Sequence[_OptimizationFixture],
    ) -> PromptCandidate:
        """Run the candidate on each fixture and return its PromptCandidate."""
        scores: list[float] = []
        passed = 0
        for fx in fixtures:
            request = LLMRequest(
                model=self._model,
                system_prompt=system_prompt,
                user_prompt=fx.user_prompt,
            )
            response = self._gateway.complete(request)
            score = self._scorer.score(
                fx.name, response.content, fx.expected_class,
            )
            scores.append(score.structural_pass)
            if score.structural_pass == 1.0:
                passed += 1
        mean = sum(scores) / len(scores) if scores else 0.0
        return PromptCandidate(
            name=candidate_name, system_prompt=system_prompt,
            mean_score=mean, fixtures_passed=passed,
            fixtures_total=len(fixtures),
        )

    def select_best(
        self,
        candidates: Sequence[PromptCandidate],
    ) -> PromptCandidate:
        """Return the highest-mean-score candidate (ties → first listed)."""
        if not candidates:
            raise ValueError("no candidates supplied")
        return max(candidates, key=lambda c: c.mean_score)


def make_fixture(
    name: str, user_prompt: str, expected_class: str,
) -> _OptimizationFixture:
    """Public factory for OptimizationFixture (kept private otherwise)."""
    return _OptimizationFixture(
        name=name, user_prompt=user_prompt, expected_class=expected_class,
    )
