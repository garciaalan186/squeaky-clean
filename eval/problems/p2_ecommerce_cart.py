"""P2 E-Commerce Cart: exercises Strategy pattern + multi-class collaboration."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P2: ProblemSpec = ProblemSpec(
    id="P2",
    tier=2,
    slug="ecommerce_cart",
    description=(
        "Shopping cart that holds items with prices and quantities, "
        "calculates totals, and applies pluggable discount strategies "
        "(percentage-based and fixed-amount). Discounts cannot reduce "
        "the total below zero."
    ),
    required_bounded_contexts=["cart"],
    acceptance_criteria=[
        "Given product 'Widget' at price 10, When add_item is called, Then the cart item_count is 1",
        "Given a cart with 'Widget' at 10 and 'Gadget' at 20, When calculate_total is called, Then total is 30",
        "Given a cart with one item, When remove_item is called, Then item_count is 0",
        "Given an empty cart, When calculate_total is called, Then total is 0",
        "Given a cart with total 100, When apply_discount is called with a 10 percent discount, Then the result is 90",
        "Given a cart with total 100, When apply_discount is called with a fixed 15 discount, Then the result is 85",
        "Given a cart with total 50, When apply_discount is called with a fixed 60 discount, Then the result is 0",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(6, 15),
    required_patterns=["Entity", "ValueObject", "Strategy", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 replicates, runs 454-456 (2026-07-30), seeds 0-2.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.0,
        functional_pass_mean=1.0, functional_pass_stddev=0.0,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0482, cost_usd_stddev=0.0436,
        model_routing=(
            "architect=claude-sonnet-5",
            "fixer=claude-sonnet-5",
            "icp=claude-haiku-4-5-20251001",
            "manager=claude-sonnet-5",
        ),
        calibrated_run="meta-evaluation_454_20260730-163813",
    ),
)
