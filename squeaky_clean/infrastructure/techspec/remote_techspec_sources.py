"""RemoteTechSpecSources: MCP + allowlisted-web fetch sources (H4 chain)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.generation.techspec.tech_spec_html_extractor import (
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned
from squeaky_clean.domain.value_objects.tech_spec_resolution import TechSpecResolution
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_fetch import fetch_one
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    AllowlistRegistry,
    FetchAttempt,
)
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import TechSpecCacheMetadata


class RemoteTechSpecSources:
    """The two network-backed sources of the resolution chain.

    ``None`` from either method means "source not applicable" (no fetcher
    wired / no allowlisted URLs); a reasoned failure object means the
    source was tried and must be logged (R6.8 — never degrade silently).
    """

    def __init__(
        self, mcp: TechDocFetcher | None, web: TechDocFetcher | None,
        extractor: TechSpecHTMLExtractor, validator: TechSpecValidator,
        cache: TechSpecCacheMetadata, allowlists: AllowlistRegistry,
    ) -> None:
        self._mcp, self._web = mcp, web
        self._extractor, self._validator = extractor, validator
        self._cache, self._allowlists = cache, allowlists

    def fetch_mcp(self, a: FetchAttempt, path: Path) -> TechSpecResolution | None:
        """One MCP fetch of the canonical spec path; None when not wired."""
        if self._mcp is None:
            return None
        url = f"{a.category}/{a.technology}/{a.version}.json"
        return fetch_one(self._mcp, url, a, is_html=False,
                         extractor=self._extractor, validator=self._validator,
                         cache=self._cache, cache_path=path)

    def fetch_web(self, a: FetchAttempt, path: Path) -> TechSpecResolution | None:
        """Try every allowlisted URL; aggregate reasons when all fail."""
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
