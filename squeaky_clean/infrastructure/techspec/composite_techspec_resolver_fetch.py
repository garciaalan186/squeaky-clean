"""Fetch/cache outcome helpers for CompositeTechSpecResolver (R6.8).

Explicit outcomes: ``TechSpec`` on success, ``TechSpecFetchFailed`` /
``TechSpecPoisoned`` carrying a reason on error. ``None`` means ONLY a clean
cache miss — never an error, so the resolver can log every failure loudly.
"""

from pathlib import Path

from squeaky_clean.application.generation.techspec.tech_doc_sanitizer import (
    TechDocPoisonedError,
    sanitize,
)
from squeaky_clean.application.generation.techspec.tech_spec_html_extractor import (
    TechDocFormatUnknownError,
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetcher, TechDocFetchError
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned
from squeaky_clean.domain.value_objects.tech_spec_resolution import TechSpecResolution
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    FetchAttempt,
    build_from_payload,
    spec_to_dict,
)
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import TechSpecCacheMetadata


def fetch_one(
    fetcher: TechDocFetcher, url: str, attempt: FetchAttempt,
    *, is_html: bool, extractor: TechSpecHTMLExtractor,
    validator: TechSpecValidator, cache: TechSpecCacheMetadata,
    cache_path: Path,
) -> TechSpecResolution:
    """Fetch + sanitize + build + cache one URL; failures carry a reason."""
    try:
        clean = sanitize(fetcher.fetch(url))
        outcome = build_from_payload(clean, attempt, is_html, extractor, validator)
    except TechDocPoisonedError as exc:
        return TechSpecPoisoned(f"{url}: {exc}")
    except (TechDocFetchError, TechDocFormatUnknownError,
            ValueError, TypeError) as exc:
        return TechSpecFetchFailed(f"{url}: {exc}")
    if isinstance(outcome, TechSpecPoisoned):
        return TechSpecPoisoned(f"{url}: {outcome.reason}")
    if isinstance(outcome, TechSpecFetchFailed):
        return TechSpecFetchFailed(f"{url}: {outcome.reason}")
    cache.write(
        cache_path, spec_to_dict(outcome, clean, is_html), (url,), cache.now_utc(),
    )
    return outcome


def try_cache(
    cache: TechSpecCacheMetadata, cache_path: Path, *, stale: bool,
) -> TechSpec | TechSpecFetchFailed | None:
    """Cached TechSpec within TTL (grace window when ``stale``).

    None = clean miss; a corrupt entry returns a reasoned failure instead
    of being silently skipped.
    """
    entry = cache.read(cache_path)
    if entry is None:
        return None
    now = cache.now_utc()
    within = (
        entry.is_stale_tolerant(now, cache.ttl_days)
        if stale else entry.is_fresh(now)
    )
    if not within:
        return None
    label = "stale-cache" if stale else "fresh-cache"
    try:
        return TechSpecBuilder().build(entry.spec)
    except (ValueError, TypeError) as exc:
        return TechSpecFetchFailed(f"{label} entry rejected: {exc}")
