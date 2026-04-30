"""Tests for InfrastructureChoiceArchitect (H3)."""

from pathlib import Path

import pytest

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.infrastructure_choice_architect import (
    InfrastructureChoiceArchitect,
    NoCandidatesAvailableError,
)
from squeaky_clean.application.use_cases.mcda_registry import MCDARegistry
from squeaky_clean.application.use_cases.mcda_scorer import MCDAScorer
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCORES_ROOT = _REPO_ROOT / "eval" / "mcda_scores"


class _StubGateway(LLMGateway):
    def __init__(self, content: str = "Highest weighted score; managed posture.") -> None:
        self.content = content
        self.calls: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(
            content=self.content, input_tokens=10, output_tokens=8,
            cost_usd=0.0001, duration_ms=5,
        )


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def test_decide_returns_winner_with_rationale() -> None:
    arch = InfrastructureChoiceArchitect(
        _StubGateway(), MCDARegistry(_SCORES_ROOT), MCDAScorer(),
    )
    choice = arch.decide(_problem(), "blob_storage")
    # bundled blob_storage scores: s3 wins (4.05) under default weights
    assert choice.category == "blob_storage"
    assert choice.technology == "s3"
    assert choice.version_pin == "boto3==1.34"
    assert "managed posture" in choice.rationale.lower()


def test_rationale_truncated_to_50_words() -> None:
    long = "word " * 80
    arch = InfrastructureChoiceArchitect(
        _StubGateway(long), MCDARegistry(_SCORES_ROOT), MCDAScorer(),
    )
    choice = arch.decide(_problem(), "blob_storage")
    assert len(choice.rationale.split()) == 50


def test_decide_is_deterministic_with_stub_gateway() -> None:
    g1 = _StubGateway("rationale text"); g2 = _StubGateway("rationale text")
    a = InfrastructureChoiceArchitect(g1, MCDARegistry(_SCORES_ROOT), MCDAScorer()).decide(_problem(), "blob_storage")
    b = InfrastructureChoiceArchitect(g2, MCDARegistry(_SCORES_ROOT), MCDAScorer()).decide(_problem(), "blob_storage")
    assert a == b


def test_no_candidates_raises(tmp_path: Path) -> None:
    (tmp_path / "ghost.json").write_text(
        '{"category": "ghost", "candidates": []}',
    )
    arch = InfrastructureChoiceArchitect(
        _StubGateway(), MCDARegistry(tmp_path), MCDAScorer(),
    )
    with pytest.raises(NoCandidatesAvailableError):
        arch.decide(_problem(), "ghost")
