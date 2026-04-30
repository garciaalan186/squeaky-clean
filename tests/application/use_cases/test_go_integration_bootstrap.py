"""Tests for GoIntegrationBootstrap."""

from pathlib import Path

from squeaky_clean.application.use_cases.go_integration_bootstrap import (
    GoIntegrationBootstrap,
)
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def test_bootstrap_writes_gitignore_and_creates_dir(tmp_path: Path) -> None:
    out = tmp_path / "proj"
    GoIntegrationBootstrap(LocalFileSystem()).bootstrap(out)
    assert out.is_dir()
    gitignore = out / ".gitignore"
    assert gitignore.exists()
    body = gitignore.read_text()
    assert "vendor/" in body
    assert "*.test" in body


def test_bootstrap_is_idempotent(tmp_path: Path) -> None:
    bootstrap = GoIntegrationBootstrap(LocalFileSystem())
    bootstrap.bootstrap(tmp_path)
    bootstrap.bootstrap(tmp_path)
    assert (tmp_path / ".gitignore").exists()


def test_bootstrap_does_not_write_init_py(tmp_path: Path) -> None:
    GoIntegrationBootstrap(LocalFileSystem()).bootstrap(tmp_path)
    assert not (tmp_path / "__init__.py").exists()
    assert not (tmp_path / "src" / "__init__.py").exists()
