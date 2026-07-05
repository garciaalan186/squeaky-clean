"""Tests for LlmPatternTiebreaker: cache replay + hallucination guard."""

from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.recovery.llm_pattern_tiebreaker import (
    LlmPatternTiebreaker,
)
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.infrastructure.cache.content_addressed_cache import (
    ContentAddressedCache,
)
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_CANDIDATES: tuple[PatternName, ...] = ("DomainEvent", "Entity")
_RECORD = ClassRecord(
    fqn="app.OrderPlacedEvent", bases=(), methods=("at()",),
    fields=("id: str",), imports=(), decorators=(),
)


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content: str = content
        self.calls: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return LLMResponse(
            content=self._content, input_tokens=10, output_tokens=2,
            cost_usd=0.0, duration_ms=1,
        )


def _deps(gateway: LLMGateway) -> LLMCallDeps:
    return LLMCallDeps(
        gateway=gateway, router=ModelRouter({ModelTier.ICP: "test-model"}),
        recorder=LLMUsageRecorder(),
    )


def test_resolves_to_named_candidate(tmp_path: Path) -> None:
    gateway = _StubGateway("Entity")
    tb = LlmPatternTiebreaker(_deps(gateway), ContentAddressedCache(tmp_path))
    assert tb.resolve(_RECORD, LayerType.DOMAIN, _CANDIDATES) == "Entity"
    assert gateway.calls == 1


def test_second_call_replays_from_cache(tmp_path: Path) -> None:
    cache = ContentAddressedCache(tmp_path)
    LlmPatternTiebreaker(_deps(_StubGateway("Entity")), cache).resolve(
        _RECORD, LayerType.DOMAIN, _CANDIDATES,
    )
    # Fresh gateway that would answer differently; cache must win and not call it.
    second = _StubGateway("DomainEvent")
    result = LlmPatternTiebreaker(_deps(second), cache).resolve(
        _RECORD, LayerType.DOMAIN, _CANDIDATES,
    )
    assert result == "Entity"
    assert second.calls == 0


def test_out_of_set_answer_falls_back_to_simple_class(tmp_path: Path) -> None:
    gateway = _StubGateway("Visitor")
    tb = LlmPatternTiebreaker(_deps(gateway), ContentAddressedCache(tmp_path))
    assert tb.resolve(_RECORD, LayerType.DOMAIN, _CANDIDATES) == "SimpleClass"
