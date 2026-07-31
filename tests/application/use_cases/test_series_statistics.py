"""Tests for SeriesStatistics rolling means and 2-sigma drop detection."""

from squeaky_clean.application.evaluation.eval.report.series_statistics import SeriesStatistics


def test_rolling_mean_empty_input_returns_empty() -> None:
    assert SeriesStatistics().rolling_mean([]) == []


def test_rolling_mean_uses_trailing_window() -> None:
    result = SeriesStatistics().rolling_mean([1.0, 2.0, 3.0], window=2)
    assert result == [1.0, 1.5, 2.5]


def test_rolling_mean_short_series_averages_available_values() -> None:
    result = SeriesStatistics().rolling_mean([2.0, 4.0], window=5)
    assert result == [2.0, 3.0]


def test_two_sigma_drops_short_series_returns_empty() -> None:
    assert SeriesStatistics().two_sigma_drops([1.0, 2.0]) == []


def test_two_sigma_drops_zero_sigma_returns_empty() -> None:
    assert SeriesStatistics().two_sigma_drops([5.0] * 6) == []


def test_two_sigma_drops_flags_outlier_index() -> None:
    values = [10.0] * 9 + [0.0]
    # recent mean 9.0, sigma 3.0 -> threshold 3.0; only index 9 is <= it.
    assert SeriesStatistics().two_sigma_drops(values) == [9]


def test_two_sigma_drops_scans_whole_series_not_just_lookback() -> None:
    values = [0.0] + [10.0, 11.0] * 5
    # Threshold comes from the last 10 values, but index 0 is still flagged.
    assert SeriesStatistics().two_sigma_drops(values) == [0]


def test_two_sigma_drops_respects_lookback_window() -> None:
    values = [0.0, 0.0, 0.0, 10.0, 11.0, 10.0, 11.0]
    drops = SeriesStatistics().two_sigma_drops(values, lookback=4)
    # Stats over the last 4 values only: the early zeros are flagged.
    assert drops == [0, 1, 2]
