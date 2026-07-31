"""Tests for the GoldenMetrics VO (R5.2)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics


def _golden(routing: tuple[str, ...]) -> GoldenMetrics:
    return GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.0,
        functional_pass_mean=1.0, functional_pass_stddev=0.0,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.05, cost_usd_stddev=0.01,
        model_routing=routing, calibrated_run="meta-evaluation_454",
    )


def test_routing_matches_ignores_order() -> None:
    golden = _golden(("icp=haiku", "architect=sonnet"))
    assert golden.routing_matches({"architect": "sonnet", "icp": "haiku"})


def test_routing_mismatch_on_model_change() -> None:
    golden = _golden(("architect=sonnet", "icp=haiku"))
    assert not golden.routing_matches({"architect": "opus", "icp": "haiku"})


def test_routing_mismatch_on_missing_tier() -> None:
    golden = _golden(("architect=sonnet", "icp=haiku"))
    assert not golden.routing_matches({"architect": "sonnet"})
