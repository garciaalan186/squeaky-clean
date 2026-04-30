"""Fetch-and-cache helper for CompositeTechSpecResolver (kept tiny on purpose)."""

import logging
from pathlib import Path

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.tech_doc_sanitizer import TechDocPoisonedError, sanitize
from squeaky_clean.application.use_cases.tech_spec_html_extractor import (
    TechDocFormatUnknownError,
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher, TechDocFetchError
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecUnresolvableError
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    FetchAttempt,
    build_from_payload,
    spec_to_dict,
)
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import TechSpecCacheMetadata

_LOG = logging.getLogger(__name__)


def fetch_one(
    fetcher: TechDocFetcher, url: str, attempt: FetchAttempt,
    *, is_html: bool, extractor: TechSpecHTMLExtractor,
    validator: TechSpecValidator, cache: TechSpecCacheMetadata,
    cache_path: Path,
) -> TechSpec | None:
    """Fetch + sanitize + build + cache one URL; None on any failure."""
    try:
        clean = sanitize(fetcher.fetch(url))
        spec = build_from_payload(clean, attempt, is_html, extractor, validator)
    except (TechDocFetchError, TechDocPoisonedError,
            TechDocFormatUnknownError, ValueError, TypeError) as exc:
        _LOG.warning("source rejected for %s: %s", url, exc)
        return None
    if spec is None:
        return None
    cache.write(
        cache_path, spec_to_dict(spec, clean, is_html), (url,), cache.now_utc(),
    )
    return spec


def try_fresh_cache(
    cache: TechSpecCacheMetadata, cache_path: Path,
) -> TechSpec | None:
    """Return cached TechSpec if entry exists and is within TTL; else None."""
    entry = cache.read(cache_path)
    if entry is None or not entry.is_fresh(cache.now_utc()):
        return None
    try:
        return TechSpecBuilder().build(entry.spec)
    except (ValueError, TypeError):
        return None


def fail_or_stale(
    cache: TechSpecCacheMetadata, cache_path: Path, attempt: FetchAttempt,
) -> TechSpec:
    """Return stale-tolerant cached spec if any; else raise loudly."""
    entry = cache.read(cache_path)
    if entry is not None and entry.is_stale_tolerant(
        cache.now_utc(), cache.ttl_days,
    ):
        try:
            return TechSpecBuilder().build(entry.spec)
        except (ValueError, TypeError):
            pass
    raise TechSpecUnresolvableError(
        f"no TechSpec for ({attempt.category}, {attempt.technology}, "
        f"{attempt.version}); add a bundled snapshot at eval/tech_specs/"
        f"{attempt.category}/{attempt.technology}/{attempt.version}.json"
    )
