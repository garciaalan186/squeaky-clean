"""Tests for DependencyBuilder wiring (no LLM calls are made)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="P0", tier=0, slug="calc", description="x",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def test_build_wires_python_run_dependencies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    router = ModelRouter()
    rc = RunConfig(seed=7)
    deps = DependencyBuilder().build(router, _problem(), rc)
    assert deps.run_config is rc
    assert deps.model_router is router
    assert isinstance(deps.test_runner, PytestRunner)
    assert deps.toolkit is not None
    assert deps.toolkit.language is TargetLanguage.PYTHON
    # infrastructure_mode defaults to "manual": no techspec resolver wired.
    assert deps.tech_spec_resolver is None


def test_icp_router_promotes_java_icps_to_the_manager_model() -> None:
    base = ModelRouter()
    routed = DependencyBuilder._icp_router(base, TargetLanguage.JAVA)
    assert routed.route(ModelTier.ICP) == base.route(ModelTier.MANAGER)
    assert routed.route(ModelTier.ARCHITECT) == base.route(ModelTier.ARCHITECT)


def test_icp_router_is_passthrough_for_non_java() -> None:
    base = ModelRouter()
    assert DependencyBuilder._icp_router(base, TargetLanguage.PYTHON) is base


def test_inner_gateway_prefers_sdk_only_when_api_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(
        DependencyBuilder._select_inner_gateway(RunConfig()), ClaudeCLIGateway,
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert isinstance(
        DependencyBuilder._select_inner_gateway(RunConfig()), AnthropicSDKGateway,
    )
