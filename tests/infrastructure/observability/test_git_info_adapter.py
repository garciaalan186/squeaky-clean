"""Unit tests for GitInfoAdapter."""

import subprocess

import pytest

from squeaky_clean.domain.interfaces.provenance.git_info import GitInfo
from squeaky_clean.infrastructure.observability.git_info_adapter import GitInfoAdapter


def test_implements_port() -> None:
    assert isinstance(GitInfoAdapter(), GitInfo)


def test_returns_sha_or_unknown() -> None:
    sha = GitInfoAdapter().head_sha()
    assert sha == "unknown" or (len(sha) == 40 and sha.isalnum())


def test_git_absent_degrades_to_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(*args: object, **kwargs: object) -> object:
        raise OSError("git not found")

    monkeypatch.setattr(subprocess, "run", _boom)
    assert GitInfoAdapter().head_sha() == "unknown"
