"""Tests for MetaEvalPaths."""

from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.meta_eval_paths import MetaEvalPaths


def test_allocate_creates_monotonic_run_dir(tmp_path: Path) -> None:
    p1 = MetaEvalPaths(tmp_path).allocate()
    p2 = MetaEvalPaths(tmp_path).allocate()
    assert p1.exists() and p2.exists()
    assert p1.name.startswith("meta-evaluation_001_")
    assert p2.name.startswith("meta-evaluation_002_")


def test_problem_set_dir_without_allocate_raises(tmp_path: Path) -> None:
    paths = MetaEvalPaths(tmp_path)
    with pytest.raises(RuntimeError):
        paths.problem_set_dir(0, "calc")


def test_problem_set_dir_creates_child(tmp_path: Path) -> None:
    paths = MetaEvalPaths(tmp_path)
    run_dir = paths.allocate()
    ps = paths.problem_set_dir(0, "calc")
    assert ps.exists()
    assert ps.parent == run_dir
    assert ps.name == "problem-set-0-calc-code"
