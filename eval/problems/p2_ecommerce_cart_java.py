"""P2 E-Commerce Cart (Java)."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P2JAVA: ProblemSpec = ProblemSpec(
    id="P2JAVA",
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
    target_language=TargetLanguage.JAVA,
)
