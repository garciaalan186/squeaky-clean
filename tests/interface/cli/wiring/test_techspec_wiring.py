"""Tests for TechSpecWiring (resolver + choice architect gating)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver import (
    CompositeTechSpecResolver,
)
from squeaky_clean.interface.cli.wiring.techspec_wiring import TechSpecWiring
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


def test_resolver_is_none_when_infrastructure_mode_manual() -> None:
    assert TechSpecWiring().resolver(RunConfig(), JSONLogger()) is None


def test_resolver_is_composite_when_auto_and_schema_present() -> None:
    rc = RunConfig(infrastructure_mode="auto")
    resolver = TechSpecWiring().resolver(rc, JSONLogger())
    assert isinstance(resolver, CompositeTechSpecResolver)


def test_choice_architect_requires_auto_and_inference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    ctx = WiringContext.create(ModelRouter(), RunConfig())
    wiring = TechSpecWiring()
    assert wiring.choice_architect(RunConfig(), ctx.call_deps) is None
    rc_auto = RunConfig(infrastructure_mode="auto")
    assert wiring.choice_architect(rc_auto, ctx.call_deps) is None
