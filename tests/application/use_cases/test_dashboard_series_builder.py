"""Tests for DashboardSeriesBuilder metric-series extraction."""

from squeaky_clean.application.evaluation.eval.report.dashboard_series_builder import (
    DashboardSeriesBuilder,
)
from squeaky_clean.application.evaluation.eval.run.run_metrics_snapshot import RunMetricsSnapshot


def _snap(run: int, metrics: dict[str, float | int]) -> RunMetricsSnapshot:
    return RunMetricsSnapshot(run_number=run, timestamp=f"2026073{run}-000000",
                              metrics=metrics, problem_id="P0")


def test_build_returns_standard_keys_plus_cache_hit_ratio() -> None:
    series = DashboardSeriesBuilder().build(())
    names = [s.name for s in series]
    assert len(names) == 9
    assert names[0] == "tests_pass"
    assert names[-1] == "cache_hit_ratio"
    assert all(s.values == () and s.labels == () for s in series)


def test_series_carries_values_labels_and_rolling_mean() -> None:
    snaps = (_snap(1, {"tests_pass": 0.5}), _snap(2, {"tests_pass": 1.0}))
    series = {s.name: s for s in DashboardSeriesBuilder().build(snaps)}
    tp = series["tests_pass"]
    assert tp.labels == ("1", "2")
    assert tp.values == (0.5, 1.0)
    assert tp.rolling_mean == (0.5, 0.75)
    assert tp.regressions == ()


def test_snapshots_missing_a_metric_are_skipped() -> None:
    snaps = (_snap(1, {"tests_pass": 0.5}), _snap(2, {}),
             _snap(3, {"tests_pass": 0.75}))
    series = {s.name: s for s in DashboardSeriesBuilder().build(snaps)}
    assert series["tests_pass"].labels == ("1", "3")
    assert series["tests_pass"].values == (0.5, 0.75)


def test_cache_hit_ratio_computed_and_zero_total_skipped() -> None:
    snaps = (
        _snap(1, {"cache_hit_count": 3, "cache_miss_count": 1}),
        _snap(2, {"cache_hit_count": 0, "cache_miss_count": 0}),
        _snap(3, {"cache_hit_count": 1}),
    )
    series = {s.name: s for s in DashboardSeriesBuilder().build(snaps)}
    ratio = series["cache_hit_ratio"]
    assert ratio.labels == ("1",)
    assert ratio.values == (0.75,)


def test_regressions_report_run_numbers_not_indices() -> None:
    snaps = tuple(_snap(n, {"tests_pass": 10.0}) for n in range(5, 14))
    snaps += (_snap(14, {"tests_pass": 0.0}),)
    series = {s.name: s for s in DashboardSeriesBuilder().build(snaps)}
    assert series["tests_pass"].regressions == (14,)
