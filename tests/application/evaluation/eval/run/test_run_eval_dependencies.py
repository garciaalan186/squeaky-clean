"""Tests for RunEvalDependencies: the frozen collaborator bundle and its defaults."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import (
    RunEvalDependencies,
)
from squeaky_clean.application.evaluation.eval.run.run_manifest import RunManifest
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def test_optional_collaborators_default_to_safe_values() -> None:
    deps = build_stub_deps()
    assert deps.cost_gate is None
    assert deps.fix_failing_classes is None
    assert deps.file_system is None
    assert isinstance(deps.run_config, RunConfig)
    assert isinstance(deps.run_logger, NullRunLogger)
    assert isinstance(deps.run_manifest, RunManifest)


def test_bundle_is_frozen() -> None:
    deps = build_stub_deps()
    with pytest.raises(dataclasses.FrozenInstanceError):
        deps.cost_gate = CostGate()  # type: ignore[misc]


def test_replace_swaps_one_collaborator_without_mutating_original() -> None:
    deps = build_stub_deps()
    gate = CostGate()
    new_deps = dataclasses.replace(deps, cost_gate=gate)
    assert new_deps.cost_gate is gate
    assert deps.cost_gate is None
    assert new_deps.design_architecture is deps.design_architecture


def test_default_factories_yield_fresh_instances_per_bundle() -> None:
    a, b = build_stub_deps(), build_stub_deps()
    assert a.run_config is not b.run_config
    assert a.secret_path_scanner is not b.secret_path_scanner
    assert a.run_manifest is not b.run_manifest
    assert isinstance(a, RunEvalDependencies)
