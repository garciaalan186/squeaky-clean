"""Unit tests for DashboardGenerator."""

from pathlib import Path

from squeaky_clean.application.use_cases.dashboard_generator import DashboardGenerator


def _make_run(root: Path, name: str, summary: str) -> None:
    run = root / name
    run.mkdir(parents=True)
    (run / "SUMMARY.md").write_text(summary)


def test_generates_html_listing_known_runs(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_001_2026", "# run 1\n\n| id | tests |\n|----|-------|\n| P0 | 0.95 |\n")
    _make_run(tmp_path, "meta-evaluation_002_2026", "# run 2\n")
    target = tmp_path / "history.html"
    DashboardGenerator().generate(tmp_path, target)
    body = target.read_text()
    assert body.startswith("<!doctype html>")
    assert "meta-evaluation_001" in body
    assert "meta-evaluation_002" in body
    assert "<h1>" in body


def test_skips_dirs_without_summary(tmp_path: Path) -> None:
    no_summary = tmp_path / "meta-evaluation_999_2026"
    no_summary.mkdir(parents=True)
    target = tmp_path / "history.html"
    DashboardGenerator().generate(tmp_path, target)
    body = target.read_text()
    assert "meta-evaluation_999" not in body
