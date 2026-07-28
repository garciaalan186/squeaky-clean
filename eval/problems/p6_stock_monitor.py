"""P6 Stock Monitor: exercises the Observer pattern (subject + observers)."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
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
)
