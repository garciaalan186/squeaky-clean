"""CompositeTechSpecResolver: bundled→cache→MCP→web resolution chain (H4)."""

from collections.abc import Callable
from pathlib import Path

from squeaky_clean.application.generation.techspec.tech_spec_html_extractor import (
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher
from squeaky_clean.domain.interfaces.tech_spec_resolver import (
    TechSpecResolutionError,
    TechSpecResolver,
    TechSpecUnresolvableError,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned
from squeaky_clean.domain.value_objects.tech_spec_resolution import TechSpecResolution
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_fetch import (
    fetch_one,
    try_cache,
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
    """Wraps the filesystem resolver; adds MCP and web-fetch sources.

    R6.8 error contract: every failed source emits a RunLogger event with
    its reason, and all reasons travel into the final
    ``TechSpecResolutionError`` — resolution never degrades silently.
    """

    def __init__(
        self, fs_resolver: FilesystemTechSpecResolver,
        validator: TechSpecValidator, cache_root: Path, ttl_days: int = 30,
        mcp_fetcher: TechDocFetcher | None = None,
        web_fetcher: TechDocFetcher | None = None,
        allowlist_registry: AllowlistRegistry | None = None,
        extractor: TechSpecHTMLExtractor | None = None,
        run_logger: RunLogger | None = None,
    ) -> None:
        self._fs, self._validator, self._cache_root = fs_resolver, validator, cache_root
        self._log: RunLogger = run_logger or NullRunLogger()
        self._cache = TechSpecCacheMetadata(ttl_days, run_logger=self._log)
        self._mcp, self._web = mcp_fetcher, web_fetcher
        self._allowlists: AllowlistRegistry = allowlist_registry or {}
        self._extractor = extractor or TechSpecHTMLExtractor()

    def resolve(self, category: str, technology: str, version: str) -> TechSpec:
        """Try fs → fresh-cache → MCP → web → stale-cache; fail loudly."""
        reasons: list[str] = []
        try:
            return self._fs.resolve(category, technology, version)
        except TechSpecUnresolvableError as exc:
            self._log.event("techspec_fs_miss", reason=str(exc))
            fs_reasons = (
                exc.reasons if isinstance(exc, TechSpecResolutionError) else ()
            )
            reasons.extend(fs_reasons or (f"bundled: {exc}",))
        a = FetchAttempt(category, technology, version)
        path = self._cache_path(a)
        sources: tuple[tuple[str, Callable[[], TechSpecResolution | None]], ...] = (
            ("fresh-cache", lambda: try_cache(self._cache, path, stale=False)),
            ("mcp", lambda: self._fetch_mcp(a, path)),
            ("web", lambda: self._fetch_web(a, path)),
        )
        for name, source in sources:
            outcome = source()
            if isinstance(outcome, TechSpec):
                return outcome
            if outcome is not None:
                self._log.event(
                    "techspec_source_failed", source=name, reason=outcome.reason,
                )
                reasons.append(f"{name}: {outcome.reason}")
        return self._stale_or_raise(a, path, reasons)

    def _stale_or_raise(
        self, a: FetchAttempt, path: Path, reasons: list[str],
    ) -> TechSpec:
        """Last resort: grace-window cache entry, else raise with all reasons."""
        stale = try_cache(self._cache, path, stale=True)
        if isinstance(stale, TechSpec):
            self._log.event(
                "techspec_stale_cache_used",
                category=a.category, technology=a.technology, version=a.version,
            )
            return stale
        if stale is not None:
            self._log.event(
                "techspec_source_failed", source="stale-cache", reason=stale.reason,
            )
            reasons.append(f"stale-cache: {stale.reason}")
        self._log.event(
            "techspec_unresolvable", category=a.category,
            technology=a.technology, version=a.version, reasons=list(reasons),
        )
        raise TechSpecResolutionError(
            f"no TechSpec for ({a.category}, {a.technology}, "
            f"{a.version}); add a bundled snapshot at eval/tech_specs/"
            f"{a.category}/{a.technology}/{a.version}.json",
            tuple(reasons),
        )

    def _fetch_mcp(self, a: FetchAttempt, path: Path) -> TechSpecResolution | None:
        if self._mcp is None:
            return None
        url = f"{a.category}/{a.technology}/{a.version}.json"
        return fetch_one(self._mcp, url, a, is_html=False,
                         extractor=self._extractor, validator=self._validator,
                         cache=self._cache, cache_path=path)

    def _fetch_web(self, a: FetchAttempt, path: Path) -> TechSpecResolution | None:
        web = self._web
        if web is None:
            return None
        last: TechSpecFetchFailed | TechSpecPoisoned | None = None
        failures: list[str] = []
        for url in self._allowlists.get((a.category, a.technology), ()):
            outcome = fetch_one(web, url, a, is_html=True,
                                extractor=self._extractor, validator=self._validator,
                                cache=self._cache, cache_path=path)
            if isinstance(outcome, TechSpec):
                return outcome
            last = outcome
            failures.append(outcome.reason)
        if last is None:
            return None  # no allowlisted URLs — source not applicable
        if len(failures) == 1:
            return last
        return TechSpecFetchFailed("; ".join(failures))

    def _cache_path(self, a: FetchAttempt) -> Path:
        return self._cache_root / a.category / a.technology / f"{a.version}.json"
