"""Tests for GatewayStackFactory (gateway stack + inner gateway selection)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.budgeted_gateway import BudgetedGateway
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.interface.cli.wiring.gateway_stack_factory import GatewayStackFactory


def test_build_returns_budgeted_gateway_and_cost_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    gateway, cost_gate = GatewayStackFactory().build(RunConfig())
    assert isinstance(gateway, BudgetedGateway)
    assert isinstance(cost_gate, CostGate)


def test_cache_dir_honors_squeaky_cache_dir_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "bundle"))
    assert GatewayStackFactory._cache_dir() == tmp_path / "bundle"


def test_inner_gateway_prefers_sdk_only_when_api_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(
        GatewayStackFactory._select_inner_gateway(RunConfig()), ClaudeCLIGateway,
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert isinstance(
        GatewayStackFactory._select_inner_gateway(RunConfig()), AnthropicSDKGateway,
    )
