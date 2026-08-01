"""Tests for WiringContext.create (shared per-run collaborators)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


def test_create_shares_gateway_and_recorder_with_call_deps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    router = ModelRouter()
    rc = RunConfig(seed=3)
    ctx = WiringContext.create(router, rc)
    assert ctx.run_config is rc
    assert ctx.router is router
    assert ctx.call_deps.gateway is ctx.gateway
    assert ctx.call_deps.router is router
    assert ctx.call_deps.recorder is ctx.recorder
    assert ctx.call_deps.run_config is rc
