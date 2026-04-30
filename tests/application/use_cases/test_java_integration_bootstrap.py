"""Tests for JavaIntegrationBootstrap."""

from pathlib import Path

from squeaky_clean.application.use_cases.java_integration_bootstrap import (
    JavaIntegrationBootstrap,
)
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def test_bootstrap_writes_pom_xml(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    bootstrap = JavaIntegrationBootstrap(fs)
    bootstrap.bootstrap(tmp_path)
    pom = tmp_path / "pom.xml"
    assert pom.exists()
    content = pom.read_text()
    assert "junit-jupiter" in content
    assert "5.10.2" in content
    assert "<maven.compiler.source>11</maven.compiler.source>" in content
