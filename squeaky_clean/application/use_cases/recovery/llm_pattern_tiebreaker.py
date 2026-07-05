"""LlmPatternTiebreaker: cached, candidate-constrained LLM tie-break."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.recovery.pattern_tiebreak import PatternTiebreak
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.infrastructure.cache.content_addressed_cache import (
    ContentAddressedCache,
)

_SYSTEM = (
    "You are a design-pattern classifier. Given a class skeleton and a set "
    "of candidate patterns, reply with EXACTLY ONE pattern name from the "
    "candidates, nothing else. If unsure, pick the first candidate."
)


class LlmPatternTiebreaker(PatternTiebreak):
    """LLM adapter that breaks a pattern tie, constrained to the candidates.

    The ICP-tier call runs at temperature 0 and is keyed through a
    content-addressed cache, so a repeated project replays the same
    answer. Output outside the candidate set is rejected in favor of
    SimpleClass, so a hallucinated pattern can never leak downstream.
    """

    def __init__(self, deps: LLMCallDeps, cache: ContentAddressedCache) -> None:
        self._deps: LLMCallDeps = deps
        self._cache: ContentAddressedCache = cache

    def resolve(
        self,
        record: ClassRecord,
        layer: LayerType,
        candidates: tuple[PatternName, ...],
    ) -> PatternName:
        """Return one candidate pattern, using the cache when warm."""
        request = self._request(record, layer, candidates)
        content = self._cache.get(request.cache_key())
        if content is None:
            content = self._call(request)
        return self._pick(content, candidates)

    def _call(self, request: LLMRequest) -> str:
        response = self._deps.gateway.complete(request)
        self._deps.recorder.record(response, "icp")
        self._cache.put(request.cache_key(), response.content)
        return response.content

    def _request(
        self,
        record: ClassRecord,
        layer: LayerType,
        candidates: tuple[PatternName, ...],
    ) -> LLMRequest:
        skeleton = (
            f"class {record.fqn.rsplit('.', 1)[-1]}"
            f"({', '.join(record.bases)})\nlayer: {layer.value}\n"
            f"methods: {list(record.methods)}\nfields: {list(record.fields)}\n"
            f"decorators: {list(record.decorators)}"
        )
        prompt = f"Candidates: {', '.join(candidates)}\n\n{skeleton}"
        return LLMRequest(
            model=self._deps.router.route(ModelTier.ICP),
            system_prompt=_SYSTEM, user_prompt=prompt,
            temperature=0.0, tier="icp",
        )

    def _pick(
        self, content: str, candidates: tuple[PatternName, ...],
    ) -> PatternName:
        first = content.strip().splitlines()[0].strip() if content.strip() else ""
        for candidate in candidates:
            if first.lower() == candidate.lower():
                return candidate
        return "SimpleClass"
