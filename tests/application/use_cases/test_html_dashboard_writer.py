"""Tests for HtmlDashboardWriter."""

from html.parser import HTMLParser
from pathlib import Path

from squeaky_clean.application.dtos.run_metrics_snapshot import RunMetricsSnapshot
from squeaky_clean.application.use_cases.html_dashboard_writer import HtmlDashboardWriter


class _CountingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        self.tags += 1


def _snap(n: int, val: float, problem: str = "problem-set-0-calculator-code"
          ) -> RunMetricsSnapshot:
    return RunMetricsSnapshot(
        run_number=n, timestamp=f"2026{n:02d}01-000000",
        metrics={"tests_pass": val, "estimated_cost_usd": 0.05 * n,
                 "total_wall_clock_ms": 1000 * n,
                 "architecture_violations": 0, "agent_retries": 0,
                 "cache_hit_count": 8, "cache_miss_count": 2},
        problem_id=problem,
    )


def test_writes_file_with_chartjs_cdn(tmp_path: Path) -> None:
    snaps = tuple(_snap(i, 0.9) for i in range(1, 4))
    target = tmp_path / "dashboard.html"
    HtmlDashboardWriter().write(snaps, target)
    body = target.read_text()
    assert "chart.js@4" in body
    assert "tests_pass" in body
    assert "estimated_cost_usd" in body
    assert "cache_hit_ratio" in body
    parser = _CountingParser()
    parser.feed(body)
    assert parser.tags > 5


def test_empty_input_writes_placeholder(tmp_path: Path) -> None:
    target = tmp_path / "dashboard.html"
    HtmlDashboardWriter().write((), target)
    body = target.read_text()
    assert "No meta-evaluation runs" in body
    assert body.startswith("<!doctype html>")


def test_regression_flagging_marks_2sigma_drop(tmp_path: Path) -> None:
    snaps = tuple(_snap(i, 1.0) for i in range(1, 10))
    drop = RunMetricsSnapshot(
        run_number=10, timestamp="20261001-000000",
        metrics={"tests_pass": 0.0, "estimated_cost_usd": 0.5,
                 "total_wall_clock_ms": 10000, "architecture_violations": 0,
                 "agent_retries": 0, "cache_hit_count": 8,
                 "cache_miss_count": 2},
        problem_id="problem-set-0-calculator-code",
    )
    target = tmp_path / "dashboard.html"
    HtmlDashboardWriter().write(snaps + (drop,), target)
    body = target.read_text()
    assert "tests_pass" in body
    assert "10" in body
    assert "reg" in body
