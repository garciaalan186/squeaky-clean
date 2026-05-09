"""Tests for CargoTestRunner: result-line parsing + missing-cargo handling."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner

_RESULT_OUTPUT = (
    "running 5 tests\n"
    "test result: ok. 4 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out\n"
)


def _completed(stdout: str = "", stderr: str = "", returncode: int = 0,
               ) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["cargo", "test"], returncode=returncode,
        stdout=stdout, stderr=stderr,
    )


def test_parses_result_line(tmp_path: Path) -> None:
    with patch("subprocess.run", return_value=_completed(_RESULT_OUTPUT, "")):
        result = CargoTestRunner().run(tmp_path)
    assert result.passed == 4
    assert result.failed == 1


def test_returns_zeros_when_cargo_not_available(tmp_path: Path) -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError("cargo")):
        result = CargoTestRunner().run(tmp_path)
    assert result.passed == 0 and result.failed == 0
    assert "cargo not available" in result.raw_output


def test_returns_zeros_on_timeout(tmp_path: Path) -> None:
    err = subprocess.TimeoutExpired(cmd=["cargo"], timeout=300)
    with patch("subprocess.run", side_effect=err):
        result = CargoTestRunner().run(tmp_path)
    assert result.passed == 0
    assert "cargo timeout" in result.raw_output
