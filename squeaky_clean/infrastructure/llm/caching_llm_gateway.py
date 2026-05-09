"""CachingLLMGateway: content-addressed disk cache decorator over LLMGateway."""

import json
from pathlib import Path

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


class CachingLLMGateway(LLMGateway):
    """Wraps an LLMGateway with a persistent content-addressed cache.

    Cache key = LLMRequest.cache_key() (sha256 of model+prompts+temperature+replicate).
    Cache hits return a stored LLMResponse with cache_hit=True and cost/duration zeroed.
    """

    def __init__(
        self,
        inner: LLMGateway,
        cache_dir: Path,
    ) -> None:
        self._inner: LLMGateway = inner
        self._cache_dir: Path = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Return cached response if present, otherwise call inner and store."""
        path = self._path_for(request)
        cached = self._load(path)
        if cached is not None:
            return cached
        response = self._inner.complete(request)
        self._store(path, response)
        return response

    def _path_for(self, request: LLMRequest) -> Path:
        return self._cache_dir / f"{request.cache_key()}.json"

    def _load(self, path: Path) -> LLMResponse | None:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        return LLMResponse(
            content=str(payload.get("content", "")),
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            duration_ms=0,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
            timed_out=False,
            cache_hit=True,
        )

    def _store(self, path: Path, response: LLMResponse) -> None:
        if response.timed_out:
            return
        payload = {"content": response.content}
        path.write_text(json.dumps(payload))
