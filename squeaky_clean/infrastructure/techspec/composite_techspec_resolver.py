"""CompositeTechSpecResolver: bundled→cache→MCP→web resolution chain (H4)."""

from collections.abc import Callable
from pathlib import Path

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.tech_spec_html_extractor import TechSpecHTMLExtractor
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher
from squeaky_clean.domain.interfaces.tech_spec_resolver import (
    TechSpecResolver,
    TechSpecUnresolvableError,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_fetch import (
    fail_or_stale,
    fetch_one,
    try_fresh_cache,
)
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    AllowlistRegistry,
    FetchAttempt,
)
from squeaky_clean.infrastructure.techspec.filesystem_techspec_resolver import (
    FilesystemTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import TechSpecCacheMetadata


class CompositeTechSpecResolver(TechSpecResolver):
    """Wraps the filesystem resolver; adds MCP and web-fetch sources."""

    def __init__(
        self, fs_resolver: FilesystemTechSpecResolver,
        validator: TechSpecValidator, cache_root: Path, ttl_days: int = 30,
        mcp_fetcher: TechDocFetcher | None = None,
        web_fetcher: TechDocFetcher | None = None,
        allowlist_registry: AllowlistRegistry | None = None,
        extractor: TechSpecHTMLExtractor | None = None,
    ) -> None:
        self._fs, self._validator, self._cache_root = fs_resolver, validator, cache_root
        self._cache = TechSpecCacheMetadata(ttl_days)
        self._mcp, self._web = mcp_fetcher, web_fetcher
        self._allowlists: AllowlistRegistry = allowlist_registry or {}
        self._extractor = extractor or TechSpecHTMLExtractor()

    def resolve(self, category: str, technology: str, version: str) -> TechSpec:
        """Try fs → fresh-cache → MCP → web → stale-cache; fail loudly."""
        try:
            return self._fs.resolve(category, technology, version)
        except TechSpecUnresolvableError:
            pass
        a = FetchAttempt(category, technology, version)
        path = self._cache_path(a)
        sources: tuple[Callable[[], TechSpec | None], ...] = (
            lambda: try_fresh_cache(self._cache, path),
            lambda: self._fetch_mcp(a, path), lambda: self._fetch_web(a, path),
        )
        for source in sources:
            spec = source()
            if spec is not None:
                return spec
        return fail_or_stale(self._cache, path, a)

    def _fetch_mcp(self, a: FetchAttempt, path: Path) -> TechSpec | None:
        if self._mcp is None:
            return None
        url = f"{a.category}/{a.technology}/{a.version}.json"
        return fetch_one(self._mcp, url, a, is_html=False,
                         extractor=self._extractor, validator=self._validator,
                         cache=self._cache, cache_path=path)

    def _fetch_web(self, a: FetchAttempt, path: Path) -> TechSpec | None:
        web = self._web
        if web is None:
            return None
        for url in self._allowlists.get((a.category, a.technology), ()):
            spec = fetch_one(web, url, a, is_html=True,
                             extractor=self._extractor, validator=self._validator,
                             cache=self._cache, cache_path=path)
            if spec is not None:
                return spec
        return None

    def _cache_path(self, a: FetchAttempt) -> Path:
        return self._cache_root / a.category / a.technology / f"{a.version}.json"
