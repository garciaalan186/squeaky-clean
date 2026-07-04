"""Run pytest-cov against a generated project; parse the JSON report."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CoverageResult:
    """Coverage percentages + whether the suite ran at all."""

    line_pct: float
    branch_pct: float
    tests_runnable: bool
    failure_log: str = ""


def collect(project_dir: Path, timeout_seconds: int = 180) -> CoverageResult:
    """Install deps + run pytest --cov in `project_dir`. Best-effort.

    The function never raises; it captures any failure into `failure_log`
    so the caller can record it on BaselineComparisonMetrics rather than
    crash the comparison run.
    """
    deps_dir = project_dir / ".test-deps"
    deps_dir.mkdir(exist_ok=True)
    install_log = _try_install(project_dir, deps_dir, timeout_seconds)
    test_result = _try_run_pytest(project_dir, deps_dir, timeout_seconds)
    if not test_result.ran:
        return CoverageResult(
            line_pct=0.0,
            branch_pct=0.0,
            tests_runnable=False,
            failure_log=f"install:\n{install_log}\n\nrun:\n{test_result.log}",
        )
    cov_path = project_dir / "coverage.json"
    if not cov_path.exists():
        return CoverageResult(
            line_pct=0.0, branch_pct=0.0, tests_runnable=True, failure_log=test_result.log
        )
    return _parse_coverage_json(cov_path, test_result.log)


@dataclass(frozen=True)
class _PytestRun:
    ran: bool
    log: str


def _try_install(project_dir: Path, deps_dir: Path, timeout: int) -> str:
    """Install pytest+coverage tooling unconditionally; project deps if any."""
    req = project_dir / "requirements.txt"
    base_packages = ["coverage[toml]", "pytest", "pytest-cov"]
    args = ["pip", "install", "--target", str(deps_dir)]
    if req.exists():
        args += ["-r", str(req)]
    args += base_packages
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            cwd=str(project_dir),
        )
        return f"rc={proc.returncode}\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"install error: {exc}"


def _try_run_pytest(project_dir: Path, deps_dir: Path, timeout: int) -> _PytestRun:
    try:
        proc = subprocess.run(
            ["python3", "-m", "pytest", "tests/",
             "--cov=src", "--cov-branch",
             "--cov-report=json:coverage.json",
             "-q", "--tb=short"],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(project_dir),
            env=_pytest_env(deps_dir),
        )
        return _PytestRun(ran=True, log=f"rc={proc.returncode}\n{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        return _PytestRun(ran=False, log=f"pytest error: {exc}")


def _pytest_env(deps_dir: Path) -> dict[str, str]:
    import os
    env = dict(os.environ)
    py_path = f".:{deps_dir}"
    if "PYTHONPATH" in env:
        py_path = f"{py_path}:{env['PYTHONPATH']}"
    env["PYTHONPATH"] = py_path
    return env


def _parse_coverage_json(path: Path, log: str) -> CoverageResult:
    try:
        data = json.loads(path.read_text())
        totals = data.get("totals", {})
        line_pct = float(totals.get("percent_covered", 0.0))
        branch_pct = float(totals.get("percent_covered_branches", 0.0)) if "percent_covered_branches" in totals else 0.0
        return CoverageResult(line_pct=line_pct, branch_pct=branch_pct, tests_runnable=True, failure_log=log)
    except (json.JSONDecodeError, OSError) as exc:
        return CoverageResult(line_pct=0.0, branch_pct=0.0, tests_runnable=True, failure_log=f"coverage parse: {exc}\n{log}")
