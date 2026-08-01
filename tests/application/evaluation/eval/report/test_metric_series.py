"""Tests for the MetricSeries value object."""

import pytest

from squeaky_clean.application.evaluation.eval.report.metric_series import MetricSeries


def test_holds_series_fields() -> None:
    s = MetricSeries(
        name="tests_pass", labels=("1", "2"), values=(0.5, 1.0),
        rolling_mean=(0.5, 0.75), regressions=(2,),
    )
    assert s.name == "tests_pass"
    assert s.values == (0.5, 1.0)
    assert s.regressions == (2,)


def test_is_frozen() -> None:
    s = MetricSeries(name="x", labels=(), values=(), rolling_mean=(), regressions=())
    with pytest.raises(AttributeError):
        s.name = "y"  # type: ignore[misc]
