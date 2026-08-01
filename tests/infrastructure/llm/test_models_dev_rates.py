"""Tests for models_dev_rates (extracted from model_pricing). No live network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.llm import models_dev_rates


@pytest.fixture(autouse=True)
def _isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(models_dev_rates, "_LIVE", None)
    monkeypatch.setattr(models_dev_rates, "_CACHE", tmp_path / "models_dev.json")

    def _no_network(*args: object, **kwargs: object) -> object:
        raise OSError("network disabled in tests")

    monkeypatch.setattr(
        models_dev_rates.urllib.request, "urlopen", _no_network,
    )


def _write_cache(payload: dict[str, object]) -> None:
    models_dev_rates._CACHE.parent.mkdir(parents=True, exist_ok=True)
    models_dev_rates._CACHE.write_text(json.dumps(payload))


def test_fresh_cache_payload_yields_parsed_rates() -> None:
    _write_cache({"anthropic": {"models": {"m1": {
        "cost": {"input": 1.0, "output": 5.0,
                 "cache_write": 1.25, "cache_read": 0.1},
    }}}})
    assert models_dev_rates.live_rates() == {"m1": (1.0, 5.0, 1.25, 0.1)}


def test_offline_with_no_cache_yields_empty_rates() -> None:
    assert models_dev_rates.live_rates() == {}


def test_models_without_cost_dict_are_skipped() -> None:
    _write_cache({"anthropic": {"models": {
        "good": {"cost": {"input": 3.0, "output": 15.0}},
        "bad": {"cost": "free"},
    }}})
    rates = models_dev_rates.live_rates()
    assert "good" in rates and "bad" not in rates


def test_result_is_memoized_per_process() -> None:
    _write_cache({"anthropic": {"models": {"m1": {
        "cost": {"input": 1.0, "output": 5.0},
    }}}})
    first = models_dev_rates.live_rates()
    models_dev_rates._CACHE.unlink()
    assert models_dev_rates.live_rates() is first
