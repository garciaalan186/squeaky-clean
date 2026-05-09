"""Tests for CompositeTechSpecResolver (H4): cache coherence + e2e."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from squeaky_clean.domain.interfaces.tech_doc_fetcher import (
    TechDocFetcher,
    TechDocFetchError,
)
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecUnresolvableError
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver import (
    CompositeTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    AllowlistRegistry,
)
from squeaky_clean.infrastructure.techspec.filesystem_techspec_resolver import (
    FilesystemTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import (
    TechSpecCacheMetadata,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_AWS_HTML = (
    "<h1 class=\"awsdocs-page-title\">PutObject</h1>"
    "<a id=\"put_object\">link</a>"
)


class _StubFetcher(TechDocFetcher):
    def __init__(self, body: str | Exception) -> None:
        self.body = body
        self.calls: int = 0

    def fetch(self, url: str) -> str:
        self.calls += 1
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


def _resolver(
    root: Path, *, web: TechDocFetcher | None = None,
    allow: AllowlistRegistry | None = None, ttl_days: int = 30,
) -> CompositeTechSpecResolver:
    validator = JSONSchemaTechSpecValidator(_SCHEMA)
    fs = FilesystemTechSpecResolver(root, validator)
    return CompositeTechSpecResolver(
        fs, validator, cache_root=root / ".cache",
        ttl_days=ttl_days, web_fetcher=web, allowlist_registry=allow or {},
    )


def test_fail_loud_when_no_source_resolves(tmp_path: Path) -> None:
    res = _resolver(tmp_path)
    with pytest.raises(TechSpecUnresolvableError) as exc:
        res.resolve("blob_storage", "fictional_tech", "v1")
    msg = str(exc.value)
    assert "blob_storage" in msg and "fictional_tech" in msg and "v1" in msg
    assert "add a bundled snapshot" in msg


def test_e2e_smoke_web_fetch_extract_and_cache(tmp_path: Path) -> None:
    fetcher = _StubFetcher(_AWS_HTML)
    allow: AllowlistRegistry = {
        ("blob_storage", "s3"): (
            "https://docs.aws.amazon.com/AmazonS3/page.html",
        )
    }
    res = _resolver(tmp_path, web=fetcher, allow=allow)
    spec = res.resolve("blob_storage", "s3", "boto3==1.40")
    assert spec.technology == "s3"
    assert fetcher.calls == 1
    cache_path = (
        tmp_path / ".cache" / "blob_storage" / "s3" / "boto3==1.40.json"
    )
    assert cache_path.is_file()
    spec2 = res.resolve("blob_storage", "s3", "boto3==1.40")
    assert spec2.technology == "s3"
    assert fetcher.calls == 1


def test_unallowlisted_url_rejected(tmp_path: Path) -> None:
    fetcher = _StubFetcher(_AWS_HTML)
    res = _resolver(tmp_path, web=fetcher, allow={})
    with pytest.raises(TechSpecUnresolvableError):
        res.resolve("blob_storage", "fictional_tech", "v1")
    assert fetcher.calls == 0


def _write_cached_spec(
    cache_root: Path, ttl_days: int, *, fetched_offset_days: int = 0,
    schema_version: str = "v1",
) -> None:
    cache = TechSpecCacheMetadata(ttl_days)
    spec_dict = json.loads(
        (_TECH_ROOT / "blob_storage" / "local_disk" / "stdlib.json").read_text()
    )
    spec_dict["schema_version"] = schema_version
    spec_dict["technology"] = "fictional"
    spec_dict["version_pin"] = "v1"
    target = cache_root / "blob_storage" / "fictional" / "v1.json"
    now = datetime.now(timezone.utc) + timedelta(days=fetched_offset_days)
    cache.write(target, spec_dict, ("https://stub",), now)


def test_ttl_expiry_triggers_refetch(tmp_path: Path) -> None:
    _write_cached_spec(tmp_path / ".cache", ttl_days=30,
                       fetched_offset_days=-100)
    fetcher = _StubFetcher(_AWS_HTML)
    allow: AllowlistRegistry = {
        ("blob_storage", "fictional"): ("https://stub.example/page",),
    }
    res = _resolver(tmp_path, web=fetcher, allow=allow, ttl_days=30)
    spec = res.resolve("blob_storage", "fictional", "v1")
    assert spec.technology == "fictional"
    assert fetcher.calls == 1


def test_stale_tolerant_grace_on_outage(tmp_path: Path) -> None:
    _write_cached_spec(tmp_path / ".cache", ttl_days=30,
                       fetched_offset_days=-35)
    fetcher = _StubFetcher(TechDocFetchError("boom"))
    allow: AllowlistRegistry = {
        ("blob_storage", "fictional"): ("https://stub.example/page",),
    }
    res = _resolver(tmp_path, web=fetcher, allow=allow, ttl_days=30)
    spec = res.resolve("blob_storage", "fictional", "v1")
    assert spec.technology == "fictional"


def test_schema_version_mismatch_invalidates_cache(tmp_path: Path) -> None:
    _write_cached_spec(tmp_path / ".cache", ttl_days=30, schema_version="v2")
    fetcher = _StubFetcher(TechDocFetchError("offline"))
    allow: AllowlistRegistry = {
        ("blob_storage", "fictional"): ("https://stub.example/page",),
    }
    res = _resolver(tmp_path, web=fetcher, allow=allow, ttl_days=30)
    with pytest.raises(TechSpecUnresolvableError):
        res.resolve("blob_storage", "fictional", "v1")
