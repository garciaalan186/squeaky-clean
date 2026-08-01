"""Tests for EmissionWiring (per-problem emission stack + ICP routing)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.wiring.emission_wiring import EmissionWiring
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="P0", tier=0, slug="calc", description="x",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def test_wire_builds_toolkit_adapters_and_orchestrator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("SQUEAKY_CACHE_DIR", str(tmp_path / "cache"))
    ctx = WiringContext.create(ModelRouter(), RunConfig())
    bundle = EmissionWiring(ctx).wire(_problem())
    assert bundle.toolkit.language is TargetLanguage.PYTHON
    assert bundle.orchestrate_module is not None
    assert bundle.adapters.test_runner is not None


def test_icp_router_promotes_java_icps_to_the_manager_model() -> None:
    base = ModelRouter()
    routed = EmissionWiring._icp_router(base, TargetLanguage.JAVA)
    assert routed.route(ModelTier.ICP) == base.route(ModelTier.MANAGER)
    assert routed.route(ModelTier.ARCHITECT) == base.route(ModelTier.ARCHITECT)


def test_icp_router_is_passthrough_for_non_java() -> None:
    base = ModelRouter()
    assert EmissionWiring._icp_router(base, TargetLanguage.PYTHON) is base
