"""Tests for Metric."""

from squeaky_clean.domain.entities.metric import Metric


def test_metric_stores_name_and_value() -> None:
    m = Metric(name="tests_pass", value=0.75)
    assert m.name == "tests_pass"
    assert m.value == 0.75
