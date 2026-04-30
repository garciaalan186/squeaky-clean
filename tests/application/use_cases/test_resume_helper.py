"""Unit tests for ResumeHelper."""

from pathlib import Path

from squeaky_clean.application.use_cases.resume_helper import ResumeHelper


def test_empty_run_dir(tmp_path: Path) -> None:
    assert ResumeHelper().completed_problem_ids(tmp_path) == ()


def test_only_dirs_with_eval_report_count(tmp_path: Path) -> None:
    a = tmp_path / "problem-set-0-calculator-code"
    b = tmp_path / "problem-set-1-todos-code"
    a.mkdir(); b.mkdir()
    (a / "eval_report.json").write_text("{}")
    out = ResumeHelper().completed_problem_ids(tmp_path)
    assert "P0" not in out
    assert any("0" in x for x in out)


def test_nonexistent_run_dir_returns_empty(tmp_path: Path) -> None:
    assert ResumeHelper().completed_problem_ids(tmp_path / "nope") == ()
