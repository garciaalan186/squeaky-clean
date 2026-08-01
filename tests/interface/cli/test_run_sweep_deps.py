"""Tests for the RunSweepDeps frozen dependency bundle."""

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest

from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.run_sweep_deps import RunSweepDeps


def _deps(run_root: Path | None = None) -> RunSweepDeps:
    return RunSweepDeps(
        dependency_builder=cast(DependencyBuilder, Mock(spec=DependencyBuilder)),
        router=ModelRouter(), run_root=run_root,
    )


def test_run_root_defaults_to_none() -> None:
    deps = RunSweepDeps(
        dependency_builder=cast(DependencyBuilder, Mock(spec=DependencyBuilder)),
        router=ModelRouter(),
    )
    assert deps.run_root is None


def test_explicit_run_root_is_stored(tmp_path: Path) -> None:
    deps = _deps(run_root=tmp_path)
    assert deps.run_root == tmp_path


def test_bundle_is_frozen() -> None:
    deps = _deps()
    with pytest.raises(FrozenInstanceError):
        deps.run_root = Path(".")  # type: ignore[misc]
