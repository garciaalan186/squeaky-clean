"""Copy a Squeaky run's output into the comparison structure + score it.

Reads the framework's eval_report.json + generated source, computes a
BaselineComparisonMetrics, also runs the neutral test suite (best-effort)
for an apples-to-apples coverage figure.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.comparison.baseline_metrics import BaselineComparisonMetrics
from scripts.comparison.coverage_collector import collect
from scripts.comparison.decomposition_metrics import measure as measure_decomposition


def integrate(
    squeaky_eval_report: Path,
    target_dir: Path,
    replicate_id: int,
    framing: str,
    problem_id: str,
    neutral_tests_dir: Path | None = None,
) -> BaselineComparisonMetrics:
    """Copy the Squeaky project to `target_dir`, compute metrics, return them."""
    src_project = squeaky_eval_report.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    _copy_project(src_project, target_dir)
    report = json.loads(squeaky_eval_report.read_text())
    metrics = report.get("metrics", {})
    decomp = measure_decomposition(target_dir)
    neutral_cov = _run_neutral(target_dir, neutral_tests_dir)
    return BaselineComparisonMetrics(
        framing=framing,
        system="squeaky",
        replicate_id=replicate_id,
        problem_id=problem_id,
        tests_pass=float(metrics.get("tests_pass", 0.0)),
        compile_errors=int(metrics.get("compile_errors", 0)),
        architecture_violations=int(metrics.get("architecture_violations", 0)),
        hallucinations=int(metrics.get("hallucinations", 0)),
        tests_runnable=neutral_cov.tests_runnable,
        coverage_line_pct=neutral_cov.line_pct,
        coverage_branch_pct=neutral_cov.branch_pct,
        estimated_cost_usd=float(metrics.get("estimated_cost_usd", 0.0)),
        total_wall_clock_ms=int(metrics.get("total_wall_clock_ms", 0)),
        total_tokens_input=int(metrics.get("total_tokens_input", 0)),
        total_tokens_output=int(metrics.get("total_tokens_output", 0)),
        retry_count=int(metrics.get("agent_retries", 0)),
        avg_file_line_count=decomp.avg_file_line_count,
        max_file_line_count=decomp.max_file_line_count,
        classes_per_module=decomp.classes_per_module,
        orphan_files=decomp.orphan_files,
        prompt_template_version="squeaky-native",
        translator_version="",
        model_id="claude-sonnet-4-6+claude-haiku-4-5",
    )


def _copy_project(src: Path, dst: Path) -> None:
    """Copy the relevant files from a Squeaky run dir to the target."""
    for child in src.iterdir():
        if child.name in ("__pycache__", ".pytest_cache", ".test-deps"):
            continue
        target = dst / child.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def _run_neutral(project_dir: Path, neutral_tests_dir: Path | None):
    """Run the neutral test suite against `project_dir` (best-effort).

    If neutral_tests_dir is None, returns a CoverageResult that says tests
    didn't run; the caller records `tests_runnable=False` honestly.
    """
    from scripts.comparison.coverage_collector import CoverageResult
    if neutral_tests_dir is None:
        return CoverageResult(line_pct=0.0, branch_pct=0.0, tests_runnable=False)
    project_tests = project_dir / "tests"
    project_tests.mkdir(exist_ok=True)
    neutral_test = neutral_tests_dir / "test_acceptance.py"
    if neutral_test.exists():
        shutil.copy2(neutral_test, project_tests / "test_acceptance_neutral.py")
    return collect(project_dir, timeout_seconds=120)
