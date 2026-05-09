"""Tests for MavenTestRunner: Surefire XML parsing + missing-mvn handling."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner


def _write_surefire_xml(
    project_dir: Path, name: str, tests: int, failures: int, errors: int,
) -> None:
    reports = project_dir / "target" / "surefire-reports"
    reports.mkdir(parents=True, exist_ok=True)
    body = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<testsuite name="{name}" tests="{tests}" '
        f'failures="{failures}" errors="{errors}" skipped="0">\n'
        f'</testsuite>\n'
    )
    (reports / f"TEST-{name}.xml").write_text(body)


def _completed(stdout: str = "", stderr: str = "", returncode: int = 0,
               ) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["mvn", "-q", "test"], returncode=returncode,
        stdout=stdout, stderr=stderr,
    )


def test_maven_test_runner_instantiates() -> None:
    assert MavenTestRunner() is not None


def test_parses_surefire_xml_and_sums_across_files(tmp_path: Path) -> None:
    _write_surefire_xml(tmp_path, "FooTest", tests=3, failures=1, errors=0)
    _write_surefire_xml(tmp_path, "BarTest", tests=4, failures=0, errors=1)
    with patch("subprocess.run", return_value=_completed("done", "")):
        result = MavenTestRunner().run(tmp_path)
    assert result.passed == 5
    assert result.failed == 1
    assert result.errors == 1


def test_returns_zeros_when_mvn_not_available(tmp_path: Path) -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError("mvn")):
        result = MavenTestRunner().run(tmp_path)
    assert result.passed == 0
    assert result.failed == 0
    assert result.errors == 0
    assert "maven not available" in result.raw_output


def test_returns_zeros_on_timeout(tmp_path: Path) -> None:
    err = subprocess.TimeoutExpired(cmd=["mvn"], timeout=300)
    with patch("subprocess.run", side_effect=err):
        result = MavenTestRunner().run(tmp_path)
    assert result.passed == 0
    assert "maven timeout" in result.raw_output


def test_returns_zero_when_no_surefire_dir(tmp_path: Path) -> None:
    with patch("subprocess.run", return_value=_completed("compile failed", "")):
        result = MavenTestRunner().run(tmp_path)
    assert result.passed == 0
    assert result.failed == 0
    assert result.errors == 0


def test_factory_returns_maven_runner_for_java() -> None:
    from squeaky_clean.application.use_cases.language_test_runner_factory import (
        LanguageTestRunnerFactory,
    )
    from squeaky_clean.domain.value_objects.target_language import TargetLanguage
    runner = LanguageTestRunnerFactory().for_language(TargetLanguage.JAVA)
    assert isinstance(runner, MavenTestRunner)
