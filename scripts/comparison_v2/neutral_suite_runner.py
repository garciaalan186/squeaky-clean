"""Apply a per-problem neutral test suite to a generated project and score it.

Both Squeaky-generated and vanilla-LLM-generated projects get the SAME
test files dropped into them at the SAME location, then pytest runs against
that fixed suite. Pass-rate from this run is the symmetric correctness score.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

NEUTRAL_TEST_DIRNAME = "neutral_test"
PROBLEM_ASSETS_ROOT = Path(__file__).resolve().parents[2] / "eval" / "comparison_v2"


@dataclass(frozen=True)
class NeutralTestResult:
    applied: bool
    pytest_runnable: bool
    tests_collected: int
    tests_passed: int
    tests_failed: int
    tests_errored: int
    pass_rate: float
    failure_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def asset_dir_for(problem_slug: str) -> Path:
    return PROBLEM_ASSETS_ROOT / problem_slug / NEUTRAL_TEST_DIRNAME


def apply_neutral_suite(problem_slug: str, project_dir: Path) -> Path:
    """Copy the neutral test files into project_dir/neutral_test/.

    We isolate the neutral suite under its own directory so it never
    collides with system-generated tests (which may keep running for the
    system's own retry loop) and so pytest can target it precisely.
    """
    src = asset_dir_for(problem_slug)
    if not src.is_dir():
        raise FileNotFoundError(f"No neutral test assets for {problem_slug} at {src}")
    dst = project_dir / NEUTRAL_TEST_DIRNAME
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def run_neutral_tests(project_dir: Path, *, timeout_s: int = 60) -> NeutralTestResult:
    """Invoke pytest against the neutral_test/ dir; parse JSON report."""
    test_dir = project_dir / NEUTRAL_TEST_DIRNAME
    if not test_dir.is_dir():
        return NeutralTestResult(
            applied=False, pytest_runnable=False, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=0, pass_rate=0.0,
            failure_reason="neutral_test directory not present",
        )
    report_path = project_dir / "neutral_test_report.json"
    if report_path.exists():
        report_path.unlink()
    cmd = [
        sys.executable, "-m", "pytest", str(test_dir),
        "--json-report", f"--json-report-file={report_path}",
        "--no-header", "-q", "--tb=line",
    ]
    try:
        proc = subprocess.run(
            cmd, cwd=project_dir, capture_output=True, text=True,
            timeout=timeout_s, check=False,
        )
    except subprocess.TimeoutExpired:
        return NeutralTestResult(
            applied=True, pytest_runnable=False, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=0, pass_rate=0.0,
            failure_reason=f"pytest timed out after {timeout_s}s",
        )
    if not report_path.exists():
        # pytest-json-report missing or pytest crashed before plugin loaded.
        # Try to install pytest-json-report once and re-run.
        if "pytest-json-report" in proc.stderr or "json-report" in proc.stderr or proc.returncode != 0:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "pytest-json-report", "pytest"],
                    capture_output=True, text=True, timeout=120, check=False,
                )
                proc = subprocess.run(
                    cmd, cwd=project_dir, capture_output=True, text=True,
                    timeout=timeout_s, check=False,
                )
            except subprocess.TimeoutExpired:
                pass
    if not report_path.exists():
        return NeutralTestResult(
            applied=True, pytest_runnable=False, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=0, pass_rate=0.0,
            failure_reason=f"pytest produced no JSON report; stderr_head={proc.stderr[:200]!r}",
        )
    try:
        report = json.loads(report_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return NeutralTestResult(
            applied=True, pytest_runnable=False, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=0, pass_rate=0.0,
            failure_reason=f"could not parse report: {exc}",
        )
    summary = report.get("summary", {})
    collected = int(summary.get("total", 0) or summary.get("collected", 0))
    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    errored = int(summary.get("error", 0))
    if collected == 0:
        return NeutralTestResult(
            applied=True, pytest_runnable=True, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=errored, pass_rate=0.0,
            failure_reason="no tests collected (likely import-time failure in conftest)",
        )
    pass_rate = passed / collected
    return NeutralTestResult(
        applied=True, pytest_runnable=True, tests_collected=collected,
        tests_passed=passed, tests_failed=failed, tests_errored=errored,
        pass_rate=pass_rate,
    )


def apply_and_score(problem_slug: str, project_dir: Path) -> NeutralTestResult:
    try:
        apply_neutral_suite(problem_slug, project_dir)
    except FileNotFoundError as exc:
        return NeutralTestResult(
            applied=False, pytest_runnable=False, tests_collected=0,
            tests_passed=0, tests_failed=0, tests_errored=0, pass_rate=0.0,
            failure_reason=str(exc),
        )
    return run_neutral_tests(project_dir)
