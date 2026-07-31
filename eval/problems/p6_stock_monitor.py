"""P6 Stock Monitor: exercises the Observer pattern (subject + observers)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P6: ProblemSpec = ProblemSpec(
    id="P6",
    tier=6,
    slug="stock_monitor",
    description=(
        "A stock price monitor where investors subscribe to a stock. When the "
        "stock price updates, every subscribed investor is notified and records "
        "the new price. Investors can subscribe and unsubscribe; an unsubscribed "
        "investor receives no further notifications. The stock is the subject and "
        "investors are observers."
    ),
    required_bounded_contexts=["monitoring"],
    acceptance_criteria=[
        "Given a stock 'ACME' and a subscribed investor, When the price updates to 100, Then the investor last_price is 100",
        "Given a stock with two subscribed investors, When the price updates to 50, Then both investors last_price is 50",
        "Given a subscribed investor who then unsubscribes, When the price updates to 75, Then the investor last_price is unchanged",
        "Given a stock with no subscribers, When the price updates to 10, Then no error is raised",
        "Given an investor subscribed to a stock, When subscribe is called again for the same investor, Then a single notification still sets last_price once",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(4, 12),
    required_patterns=["Entity", "ValueObject", "Observer", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.8333, tests_pass_stddev=0.2887,
        functional_pass_mean=0.8333, functional_pass_stddev=0.2887,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0617, cost_usd_stddev=0.0337,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_494_20260730-232833",
    ),
)
