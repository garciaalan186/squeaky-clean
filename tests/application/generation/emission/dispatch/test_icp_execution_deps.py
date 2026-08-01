"""Tests for the IcpExecutionDeps frozen dependency bundle."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.generation.emission.dispatch.icp_execution_deps import (
    IcpExecutionDeps,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier


class _StubGateway(LLMGateway):
    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="", input_tokens=0, output_tokens=0, cost_usd=0.0, duration_ms=0,
        )


class _StubRouter(ModelRoutingPolicy):
    def route(self, tier: ModelTier) -> str:
        return "stub-model"


def test_stores_gateway_and_router_by_identity() -> None:
    gateway, router = _StubGateway(), _StubRouter()
    deps = IcpExecutionDeps(gateway=gateway, router=router)
    assert deps.gateway is gateway
    assert deps.router is router


def test_run_config_defaults_to_fresh_default_run_config() -> None:
    deps = IcpExecutionDeps(gateway=_StubGateway(), router=_StubRouter())
    assert deps.run_config == RunConfig()


def test_explicit_run_config_is_kept() -> None:
    rc = RunConfig(seed=7, replicate_id=3)
    deps = IcpExecutionDeps(gateway=_StubGateway(), router=_StubRouter(), run_config=rc)
    assert deps.run_config is rc


def test_bundle_is_frozen() -> None:
    deps = IcpExecutionDeps(gateway=_StubGateway(), router=_StubRouter())
    with pytest.raises(FrozenInstanceError):
        deps.run_config = RunConfig()  # type: ignore[misc]
