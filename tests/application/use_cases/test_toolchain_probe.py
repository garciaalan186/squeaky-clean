"""Tests for toolchain_probe (R5.9)."""

from squeaky_clean.application.evaluation.eval.run import toolchain_probe
from squeaky_clean.application.evaluation.eval.run.toolchain_probe import (
    _first_line,
    probe,
)


def test_probe_reports_every_known_tool() -> None:
    versions = probe()
    assert set(versions) == {"node", "npm", "javac", "mvn", "go", "cargo"}
    assert all(isinstance(v, str) and v for v in versions.values())


def test_missing_tool_reports_absent() -> None:
    assert _first_line(["definitely-not-a-real-tool-xyz"]) == "absent"


def test_first_line_only(monkeypatch) -> None:  # noqa: ANN001
    class _Fake:
        stdout = "v20.1.0\nextra noise\n"
        stderr = ""

    monkeypatch.setattr(
        toolchain_probe.subprocess, "run", lambda *a, **k: _Fake(),
    )
    assert _first_line(["node", "--version"]) == "v20.1.0"
