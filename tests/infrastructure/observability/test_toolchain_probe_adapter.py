"""Unit tests for ToolchainProbeAdapter."""

import subprocess

import pytest

from squeaky_clean.domain.interfaces.provenance.toolchain_info import ToolchainInfo
from squeaky_clean.infrastructure.observability.toolchain_probe_adapter import (
    ToolchainProbeAdapter,
)

_EXPECTED_TOOLS = {"node", "npm", "javac", "mvn", "go", "cargo"}


def test_implements_port() -> None:
    assert isinstance(ToolchainProbeAdapter(), ToolchainInfo)


def test_probes_every_expected_tool() -> None:
    versions = ToolchainProbeAdapter().versions()
    assert set(versions) == _EXPECTED_TOOLS
    assert all(isinstance(v, str) and v for v in versions.values())


def test_absent_tool_reports_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(*args: object, **kwargs: object) -> object:
        raise OSError("not on PATH")

    monkeypatch.setattr(subprocess, "run", _boom)
    versions = ToolchainProbeAdapter().versions()
    assert set(versions.values()) == {"absent"}
