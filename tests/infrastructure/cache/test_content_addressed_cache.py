"""Tests for ContentAddressedCache."""

from pathlib import Path

from squeaky_clean.infrastructure.cache.content_addressed_cache import (
    ContentAddressedCache,
)


def test_miss_returns_none(tmp_path: Path) -> None:
    assert ContentAddressedCache(tmp_path).get("deadbeef") is None


def test_put_then_get_round_trips(tmp_path: Path) -> None:
    cache = ContentAddressedCache(tmp_path)
    cache.put("abcd1234", "Entity")
    assert cache.get("abcd1234") == "Entity"


def test_value_is_sharded_by_key_prefix(tmp_path: Path) -> None:
    ContentAddressedCache(tmp_path).put("abcd1234", "x")
    assert (tmp_path / "ab" / "abcd1234.txt").exists()
