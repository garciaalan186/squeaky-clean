"""Tests for RustIntegrationBootstrap."""

from pathlib import Path

from squeaky_clean.application.use_cases.rust_integration_bootstrap import (
    RustIntegrationBootstrap,
)
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def test_bootstrap_writes_src_dir_and_gitignore(tmp_path: Path) -> None:
    out = tmp_path / "proj"
    RustIntegrationBootstrap(LocalFileSystem()).bootstrap(out)
    assert (out / "src").is_dir()
    gitignore = out / ".gitignore"
    assert gitignore.exists()
    assert "target/" in gitignore.read_text()


def test_bootstrap_is_idempotent(tmp_path: Path) -> None:
    bootstrap = RustIntegrationBootstrap(LocalFileSystem())
    bootstrap.bootstrap(tmp_path)
    bootstrap.bootstrap(tmp_path)
    assert (tmp_path / "src").is_dir()
    assert (tmp_path / ".gitignore").exists()


def test_bootstrap_does_not_write_cargo_toml(tmp_path: Path) -> None:
    RustIntegrationBootstrap(LocalFileSystem()).bootstrap(tmp_path)
    assert not (tmp_path / "Cargo.toml").exists()
