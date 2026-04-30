"""Tests for GoTestRunner: JSON event parsing + missing-go handling."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner

_PASS_FAIL_JSON = (
    '{"Action":"run","Test":"TestA"}\n'
    '{"Action":"output","Test":"TestA","Output":"...\\n"}\n'
    '{"Action":"pass","Test":"TestA"}\n'
    '{"Action":"run","Test":"TestB"}\n'
    '{"Action":"fail","Test":"TestB"}\n'
    '{"Action":"pass","Test":"TestC"}\n'
)


def _completed(stdout: str = "", stderr: str = "", returncode: int = 0,
               ) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["go", "test"], returncode=returncode,
        stdout=stdout, stderr=stderr,
    )


def test_parses_pass_and_fail_events(tmp_path: Path) -> None:
    with patch("subprocess.run", return_value=_completed(_PASS_FAIL_JSON, "")):
        result = GoTestRunner().run(tmp_path)
    assert result.passed == 2
    assert result.failed == 1


def test_returns_zeros_when_go_not_available(tmp_path: Path) -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError("go")):
        result = GoTestRunner().run(tmp_path)
    assert result.passed == 0 and result.failed == 0
    assert "go not available" in result.raw_output


def test_returns_zeros_on_timeout(tmp_path: Path) -> None:
    err = subprocess.TimeoutExpired(cmd=["go"], timeout=300)
    with patch("subprocess.run", side_effect=err):
        result = GoTestRunner().run(tmp_path)
    assert result.passed == 0
    assert "go timeout" in result.raw_output
