"""Tests for RemoteTechSpecSources (extracted from CompositeTechSpecResolver)."""

from pathlib import Path

from squeaky_clean.application.generation.techspec.tech_spec_html_extractor import (
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher
from squeaky_clean.domain.interfaces.techspec.tech_doc_fetch_error import (
    TechDocFetchError,
)
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    FetchAttempt,
)
from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)
from squeaky_clean.infrastructure.techspec.remote_techspec_sources import (
    RemoteTechSpecSources,
)
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import (
    TechSpecCacheMetadata,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA = _REPO_ROOT / "eval" / "tech_specs" / "_schema.v1.json"
_ATTEMPT = FetchAttempt("blob_storage", "fictional_tech", "v1")


class _FailingFetcher(TechDocFetcher):
    def fetch(self, url: str) -> str:
        raise TechDocFetchError(f"boom: {url}")


def _sources(
    web: TechDocFetcher | None,
    allowlists: dict[tuple[str, str], tuple[str, ...]],
) -> RemoteTechSpecSources:
    return RemoteTechSpecSources(
        None, web, TechSpecHTMLExtractor(),
        JSONSchemaTechSpecValidator(_SCHEMA),
        TechSpecCacheMetadata(30), allowlists,
    )


def test_mcp_source_not_applicable_when_no_fetcher_wired(tmp_path: Path) -> None:
    sources = _sources(None, {})
    assert sources.fetch_mcp(_ATTEMPT, tmp_path / "c.json") is None


def test_web_source_not_applicable_without_allowlisted_urls(
    tmp_path: Path,
) -> None:
    sources = _sources(_FailingFetcher(), {})
    assert sources.fetch_web(_ATTEMPT, tmp_path / "c.json") is None


def test_web_failures_aggregate_every_url_reason(tmp_path: Path) -> None:
    allow = {("blob_storage", "fictional_tech"): ("http://a", "http://b")}
    sources = _sources(_FailingFetcher(), allow)
    outcome = sources.fetch_web(_ATTEMPT, tmp_path / "c.json")
    assert isinstance(outcome, TechSpecFetchFailed)
    assert "http://a" in outcome.reason and "http://b" in outcome.reason
